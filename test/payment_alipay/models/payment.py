# coding: utf-8

import json
import logging
import datetime
import time
import os
import urlparse
from urlparse import urljoin

import dateutil.parser
import pytz
from werkzeug import urls

from odoo.tools.float_utils import float_compare
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from test.payment_alipay.controllers.main import AlipayController
from test.payment_alipay.models import func


_logger = logging.getLogger(__name__)


class AcquirerAlipay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('alipay', 'Alipay')], string='Provider',
                                default='alipay', required=True)

    alipay_app_id = fields.Char('APP ID', groups='base.group_user')
    alipay_app_private_key = fields.Text('APP 私钥', groups='base.group_user')
    alipay_official_public_key = fields.Text('支付宝公钥', groups='base.group_user')

    @api.model
    def _get_alipay_urls(self, environment):
        """ Alipay URLS """
        if environment == 'prod':
            return {
                'alipay_form_url': 'https://openapi.alipay.com/gateway.do?',
            }
        else:
            return {
                'alipay_form_url': 'https://openapi.alipaydev.com/gateway.do?',
            }

    @api.multi
    def alipay_compute_fees(self, amount, currency_id, country_id):
        """ Compute Alipay fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared to
                                       the acquirer company country.
            :return float fees: computed fees
        """
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            #国内
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            #国际
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    @api.multi
    def alipay_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # 公共参数
        alipay_tx_values = dict(values)
        alipay_tx_values.update({
            # basic parameters
            'method': 'alipay.trade.page.pay',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'return_url': '%s' % urljoin(base_url, AlipayController._return_url),
            'notify_url': '%s' % urljoin(base_url, AlipayController._notify_url),
            'app_id': self.alipay_app_id,
            'version': '1.0',
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'biz_content': ''
        })

        _logger.info(alipay_tx_values)
        # 业务参数
        biz_content = {}
        # 商户订单号
        biz_content['out_trade_no'] = values['reference']
        biz_content['product_code'] = 'FAST_INSTANT_TRADE_PAY'
        biz_content['total_amount'] = values['amount']

        biz_content['subject'] = '%s: %s' % (self.company_id.name, values['reference'])
        biz_content['body'] = '%s: %s' % (self.company_id.name, values['reference'])

        # alipay_tx_values.update({'biz_content':biz_content_sign.decode('utf-8')})
        alipay_tx_values.update({'biz_content': json.dumps(biz_content)})

        subkey = ['app_id', 'method', 'version', 'charset', 'sign_type', 'timestamp', 'biz_content', 'return_url',
                  'notify_url']
        need_sign = {key: alipay_tx_values[key] for key in subkey}
        params, sign = func.buildRequestMysign(need_sign, self.alipay_app_private_key)
        alipay_tx_values.update({
            'sign': sign,
        })
        _logger.info('script_dir : %s' % (os.path.dirname(__file__)))

        print('--------testing  start---------------')
        need_sign.update({'sign': sign})
        print(need_sign)
        url = func.createLinkstringUrlencode(need_sign)
        print(url)
        alipay_url = self.alipay_get_form_action_url() + url
        print(alipay_url)
        print('--------testing  end-----------------')
        '''
        get请求指定参数+签名,就能跳转支付界面
        '''
        return alipay_tx_values

    @api.multi
    def alipay_get_form_action_url(self):
        return self._get_alipay_urls(self.environment)['alipay_form_url']


class TxAlipay(models.Model):
    _inherit = 'payment.transaction'

    alipay_txn_type = fields.Char('Transaction type')

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _alipay_form_get_tx_from_data(self, data):
        reference, txn_id = data.get('out_trade_no'), data.get('trade_no')
        if not reference or not txn_id:
            error_msg = _('Alipay: received data with missing reference (%s) or txn_id (%s)') % (reference, txn_id)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Alipay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.multi
    def _alipay_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        return invalid_parameters

    @api.multi
    def _alipay_form_validate(self, data):

        res = {
            'acquirer_reference': data.get('out_trade_no'),
            'alipay_reference': data.get('trade_no'),
            'partner_reference': data.get('seller_id')
        }
        try:
            # dateutil and pytz don't recognize abbreviations PDT/PST
            tzinfos = {
                'PST': +8 * 3600,
                'PDT': +7 * 3600,
            }
            date_validate = dateutil.parser.parse(data.get('timestamp'), tzinfos=tzinfos).astimezone(pytz.utc)
        except:
            date_validate = fields.Datetime.now()
        res.update(state='done', date_validate=date_validate)
        return self.write(res)
