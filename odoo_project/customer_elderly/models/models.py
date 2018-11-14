# -*- coding: utf-8 -*-
import logging
import requests
import lxml.html
import calendar
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import find_in_path
from odoo.tools import config
from odoo.sql_db import TestCursor
from odoo.http import request
from odoo.tools import float_is_zero, float_compare, pycompat
from datetime import datetime

from odoo.tools.misc import formatLang, format_date, ustr
from odoo.tools import config
from odoo.tools.translate import _
import time
from contextlib import closing
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError

from lxml import etree
from distutils.version import LooseVersion
from reportlab.graphics.barcode import createBarcodeDrawing
from PyPDF2 import PdfFileWriter, PdfFileReader

import math
import json
import base64
import io
import os
import tempfile
import subprocess
import re


_logger = logging.getLogger(__name__)

try:
    createBarcodeDrawing('Code128', value='foo', format='png', width=100, height=100, humanReadable=1).asString('png')
except Exception:
    pass


def _get_wkhtmltopdf_bin():
    return find_in_path('wkhtmltopdf')


# Check the presence of Wkhtmltopdf and return its version at Odoo start-up
wkhtmltopdf_state = 'install'
try:
    process = subprocess.Popen(
        [_get_wkhtmltopdf_bin(), '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
except (OSError, IOError):
    _logger.info('You need Wkhtmltopdf to print a pdf version of the reports.')
else:
    _logger.info('Will use the Wkhtmltopdf binary at %s' % _get_wkhtmltopdf_bin())
    out, err = process.communicate()
    match = re.search(b'([0-9.]+)', out)
    if match:
        version = match.group(0).decode('ascii')
        if LooseVersion(version) < LooseVersion('0.12.0'):
            _logger.info('Upgrade Wkhtmltopdf to (at least) 0.12.0')
            wkhtmltopdf_state = 'upgrade'
        else:
            wkhtmltopdf_state = 'ok'

        if config['workers'] == 1:
            _logger.info('You need to start Odoo with at least two workers to print a pdf version of the reports.')
            wkhtmltopdf_state = 'workers'
    else:
        _logger.info('Wkhtmltopdf seems to be broken.')
        wkhtmltopdf_state = 'broken'

class customer_elderly1(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    def marital_status_selection(self):
        return [('1', '己婚'), ('2', '未婚'), ('3', '離婚'), ('4', '鰥寡')]

    def sex_selection(self):
        return [('1', '男'), ('2', '女')]

    def status_selection(self):
        return [('1', '入住中'), ('2', '停用'), ('3', '等候中')]

    def leaving_reason_selection(self):
        return [('1', '去世'), ('2', '退')]
    
    def seat_selection(self):
        return [('1', '買位'), ('2', '私位')]

    cid = fields.Char('院友編號')
    seatid = fields.Selection(selection=seat_selection, string='買位/私位')
    seat_number = fields.Char('區/床號')
    

    my_credit_limit = fields.Float('The Credit Limit :')
    id_card_no = fields.Char('身分證號碼')
    status = fields.Selection(selection=status_selection, string='狀況')
    bed_no = fields.Char('區/床號')
    checkin_date = fields.Date('入住日期')
    # id_temp = fields.Char(')
    sex = fields.Selection(selection=sex_selection, string='性別')
    birthdate = fields.Date('出生年月日')
    # occupation = fields.Char('職業')
    marital_status = fields.Selection(selection=marital_status_selection, string='婚姻狀況')
    education = fields.Char('學歷')
    religion = fields.Char('宗教')
    economic_source = fields.Char('經濟來源')
    aid_amount_start_date = fields.Date('援助金額啟始日期')
    past_medical_record = fields.Text('以往病歷')
    drug_food_sensitive = fields.Text('藥物/食物敏感紀錄')
    contact_person = fields.Text('聯絡人')
    reason_for_leaving = fields.Selection(selection=leaving_reason_selection, string='離開原因')
    leaving_date = fields.Date('離開日期')
    occupation_id = fields.Many2one('wantech.occupation', string='職業')

    
    @api.multi
    def action_view_partner_payment_view(self):
        return{
            'name': _('Checks to Print'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target':'new',
            'res_model': 'account.payment',
            'context': {
                'default_payment_type': 'inbound',
                'default_journal_id':6,
                'default_amount': 0,
                'default_partner_id':self.id,
                'default_check_to_print':2,
            }
        }

        
# class productPlusDecp(models.Model):
#     _inherit = "account.invoice.report"

    #product_id = fields.Many2one('product.product', string='職業11111', readonly=True)

    # product_id =Char('職業', compute='action_open_account_invoice_report')


    # def action_open_account_invoice_report(self):
    #     sales = self.env['product.product'].search([('id', 'in', self.ids)])

    #     for record in sales:
    #         record['id'] = record['price'] + record['product_tmpl_id']
    #         return record



class seatid(models.Model):
    _name = 'wantech.seatid'
    name = fields.Char()

class occupation(models.Model):
    _name = 'wantech.occupation'
    name = fields.Char()
    # elderly_ids = fields.One2many('res.partner','occupation_id', string='Elderly')

#     _name = 'customer_elderly1.customer_elderly1'
#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class PrintPDF(models.Model):
    _name = 'wantech.printpdf'
    _description = 'PrintPDF'

    @api.multi
    def invoice_confirm(self):
        context = dict(self._context or {})
        #active_ids = self.env.context.get('active_ids', [])
        # active_ids = context.get('active_ids', []) or []
        # record2 = ""
        # for record in self.env['demo01.demo01'].browse(active_ids):
        #     logging.warning(record.name)
        #     record2 = record
        # logging.warning(record2.name)
        active_ids = self.env.context.get('active_ids', [])
        records = self.env['res.partner'].browse(active_ids)
        #logging.warning(self)
        #logging.warning(records)
        return self.env.ref('customer_elderly.report_pdf').report_action(records)


class report_account_followup_report(models.AbstractModel):
    #_name = "account.followup.report2"
    _description = "Followup Report"
    _inherit = 'account.report'


    def print_followup2(self, options, params):
        partner_id = params.get('partner')
        options['partner_id'] = partner_id
        options['pdfsize'] = "A4"
        return {
                'type': 'ir_actions_account_report_download',
                'data': {'model': 'account.followup.report2',
                         'options': json.dumps(options),
                         'output_format': 'pdf',
                         }
                }

class report_account_followup_report2(models.AbstractModel):
    _name = "account.followup.report2"
    _description = "Followup Report"
    _inherit = 'account.report'

 
    #TO BE OVERWRITTEN
    def get_columns_name(self, options):
        headers = [
                {'name': _(' 日期 '), 'class': 'date', 'style': 'text-align:center;'}, 
                {'name': _(' 收據編號 '), 'style': 'text-align:right;'}, 
                {'name': _(' 項目 '), 'style': 'text-align:right;width:100px;'}, 
                {'name': _(' 單價 '), 'class': 'number'}, 
                {'name': _(' 數量 '), 'class': 'number'}, 
                {'name': _(' 價錢 '), 'class': 'number', 'style': 'text-align:right;'}
                ]
        if self.env.context.get('print_mode'):
            headers = headers[0:6]
        return headers

    #TO BE OVERWRITTEN
    def get_lines(self, options, line_id=None):
    # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        
        if not partner:
            return []
        lang_code = partner.lang or self.env.user.lang or 'en_US'

        lines = []
        res = {}
        today = datetime.today().strftime('%Y-%m-%d')
        line_num = 0
        
        
        


        for l in partner.unreconciled_aml_ids:
            if self.env.context.get('print_mode') and l.blocked:
                continue
            currency = l.currency_id or l.company_id.currency_id
            
            
            #logging.warning(l.first_print)

            
            # if l.invoice_id.number:
            #     logging.warning(l.invoice_id.invoice_line_ids)
            #     for a in l.invoice_id.invoice_line_ids:
            #         logging.warning(a.name)
            #         logging.warning(a.partner_id)
            #         logging.warning(a.price_total)
            #         logging.warning(a.price_unit)
            #         logging.warning(a.invoice_id)
            #accountinovice = self.env['account.invoice'].search([('name', '=', l.invoice_id)]) or False
            #logging.warning(accountinovice)
            # logging.warning(accountinovice)
            # for a in accountinovice.invoice_line_ids:
            #     logging.warning(a.partner_id)

            if currency not in res:
                res[currency] = []
            res[currency].append(l)
        #  invoice_line_ids
        #accountinovice = self.env['account.invoice.line'].search([('invoice_line_ids', '=', l.)])
         
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            aml_recs = sorted(aml_recs, key=lambda aml: aml.blocked)
            for aml in aml_recs:            
                amount = aml.currency_id and aml.amount_residual_currency or aml.amount_residual
                date_due = format_date(self.env, aml.date_maturity or aml.date, lang_code=lang_code)
                total += not aml.blocked and amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                is_payment = aml.payment_id

                if is_overdue or is_payment:
                    total_issued += not aml.blocked and amount or 0
                if is_overdue:
                    date_due = {'name': date_due, 'class': 'color-red date'}
                if is_payment:
                    date_due = ''
                amount = formatLang(self.env, amount, currency_obj=currency)
                amount = amount.replace(' ', '&nbsp;') if self.env.context.get('mail') else amount
                line_num += 1
                if aml.name is not "/":
                    columns = [format_date(self.env, aml.date, lang_code=lang_code), aml.payment_id.name, aml.payment_id.item_id.name,'','', amount]
                else:
                    columns = [format_date(self.env, aml.date, lang_code=lang_code), aml.invoice_id.number, aml.payment_id.item_id.name,'','', amount]

                # if self.env.context.get('print_mode'):
                #     columns = columns[:3]+columns[5:]
                lines.append({
                    'id': aml.id,
                    'name': aml.move_id.name,
                    'caret_options': 'followup',
                    'move_id': aml.move_id.id,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'columns': [type(v) == dict and v or {'name': v} for v in columns],
                })
                

                #logging.warning(aml.invoice_id.number)
                if aml.invoice_id.number:
                    for a in aml.invoice_id.invoice_line_ids:
                        columns2 = ['','',a.name,a.price_unit,a.quantity,'']
                        # logging.warning(a.name)
                        # logging.warning(a.partner_id)
                        # logging.warning(a.price_total)
                        # logging.warning(a.price_unit)
                        # logging.warning(a.invoice_id)
                        line_num += 1
                        lines.append({
                            'id': aml.id,
                            'name': aml.move_id.name,
                            'caret_options': 'followup',
                            'move_id': aml.move_id.id,
                            'type': is_payment and 'payment' or 'unreconciled_aml',
                            'unfoldable': False,
                            'columns': [type(v) == dict and v or {'name': v} for v in columns2],
                        })
                        #logging.warning(columns2)
            totalXXX = formatLang(self.env, total, currency_obj=currency)
            totalXXX = totalXXX.replace(' ', '&nbsp;') if self.env.context.get('mail') else totalXXX
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': 'total',
                'unfoldable': False,
                'level': 0,
                'columns': [{'name': v} for v in ['']*(4 if self.env.context.get('print_mode') else 6) + [total >= 0 and _('Total Due') or '', totalXXX]],
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued, currency_obj=currency)
                total_issued = total_issued.replace(' ', '&nbsp;') if self.env.context.get('mail') else total_issued
                line_num += 1
                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total',
                    'unfoldable': False,
                    'level': 0,
                    'columns': [{'name': v} for v in ['']*(4 if self.env.context.get('print_mode') else 6) + [_('Total Overdue'), total_issued]],
                })
                
        return lines

    #TO BE OVERWRITTEN
    def get_templates(self):
        return {
                'main_template': 'customer_elderly.main_template2',
                #'line_template': 'customer_elderly.line_template2',
                #'footnotes_template': 'account_reports.footnotes_template',
                #'search_template': 'account_reports.search_template',
        }

    def get_pdf(self, options, minimal_layout=True):
        # As the assets are generated during the same transaction as the rendering of the
        # templates calling them, there is a scenario where the assets are unreachable: when
        # you make a request to read the assets while the transaction creating them is not done.
        # Indeed, when you make an asset request, the controller has to read the `ir.attachment`
        # table.
        # This scenario happens when you want to print a PDF report for the first time, as the
        # assets are not in cache and must be generated. To workaround this issue, we manually
        # commit the writes in the `ir.attachment` table. It is done thanks to a key in the context.
        if not config['test_enable']:
            self = self.with_context(commit_assetsbundle=True)

        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False

        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.user,
            'tcustomer': partner,
        }        



        
        body = self.env['ir.ui.view'].render_template(
            "account_reports.print_template",
            values=dict(rcontext),
        )
        body_html = self.with_context(print_mode=True).get_html(options)
        body = body.replace(b'<body class="o_account_reports_body_print">', b'<body class="o_account_reports_body_print">' + body_html)
        #minimal_layout = False
        if minimal_layout:
               
           # header = self.env['ir.actions.report'].render_template("customer_elderly.internal_layout", values=rcontext)
            header = self.env['wantech.report.format'].render_template("customer_elderly.internal_layout", values=rcontext)
            
            

            footer = ''
            spec_paperformat_args = {'data-report-margin-top': 0, 'data-report-header-spacing': 0}
            header = self.env['wantech.report.format'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=header))

        else:
            rcontext.update({
                    'css': '',
                    'o': self.env.user,
                    'res_company': "",
                })
            header = self.env['wantech.report.format'].render_template("web.external_layout", values=rcontext)
            header = header.decode('utf-8') # Ensure that headers and footer are correctly encoded
            spec_paperformat_args = {}
            # parse header as new header contains header, body and footer
            try:
                root = lxml.html.fromstring(header)
                match_klass = "//div[contains(concat(' ', normalize-space(@class), ' '), ' {} ')]"

                for node in root.xpath(match_klass.format('header')):
                    headers = lxml.html.tostring(node)
                    headers = self.env['wantech.report.format'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=headers))

                for node in root.xpath(match_klass.format('footer')):
                    footer = lxml.html.tostring(node)
                    footer = self.env['wantech.report.format'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=footer))
            except lxml.etree.XMLSyntaxError:
                headers = header
                footer = ''

        landscape = False
        
        if len(self.with_context(print_mode=True).get_columns_name(options)) > 5:
            landscape = True


        paperformat_id2 = self.env['wantech.report.paperformat'].search([])

        if len(paperformat_id2) == 0:
            paperformat_id2 = self.env['wantech.report.paperformat'].create({'margin_bottom': 25.0, 'default': True, 'margin_right': 7.0, 'header_spacing': 35, 'id': 3, 'create_uid': (1, 'Administrator'), 'report_ids': [], '__last_update': '2018-06-05 10:52:53', 'write_date': '2018-06-05 10:52:53', 'name': 'US Letter', 'orientation': 'Portrait', 'display_name': 'US Letter', 'page_width': 0, 'format': 'A5', 'write_uid': (1, 'Administrator'), 'margin_left': 7.0, 'dpi': 90, 'create_date': '2018-06-05 10:13:21', 'page_height':0, 'margin_top': 40.0, 'header_line': False})
        else:
            paperformat_id2 = self.env['wantech.report.paperformat'].search([('id', '=', 1)])
        # paperformat_id2 = self.env['report.paperformat'].search([('id', '=', 4)])
        # if paperformat_id2 is False:
        #    paperformat_id2 = {'margin_bottom': 25.0, 'default': True, 'margin_right': 7.0, 'header_spacing': 35, 'id': 3, 'create_uid': (1, 'Administrator'), 'report_ids': [], '__last_update': '2018-06-05 10:52:53', 'write_date': '2018-06-05 10:52:53', 'name': 'US Letter', 'orientation': 'Portrait', 'display_name': 'US Letter', 'page_width': 0, 'format': 'A5', 'write_uid': (1, 'Administrator'), 'margin_left': 7.0, 'dpi': 90, 'create_date': '2018-06-05 10:13:21', 'page_height':0, 'margin_top': 40.0, 'header_line': False}
        
        return self.env['wantech.report.format']._run_wkhtmltopdf(
            paperformat_id2,
            [body],
            header=header, 
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=spec_paperformat_args
        )
        #return self.env['ir.actions.report']._run_wkhtmltopdf([body])
    


class WantechReportFormat(models.Model):
    _name = 'wantech.report.format'
    _inherit = "ir.actions.report"

    @api.model
    def _run_wkhtmltopdf(
            self,
            paperformat_id,
            bodies,
            header=None,
            footer=None,
            landscape=False,
            specific_paperformat_args=None,
            set_viewport_size=False):
        '''Execute wkhtmltopdf as a subprocess in order to convert html given in input into a pdf
        document.

        :param bodies: The html bodies of the report, one per page.
        :param header: The html header of the report containing all headers.
        :param footer: The html footer of the report containing all footers.
        :param landscape: Force the pdf to be rendered under a landscape format.
        :param specific_paperformat_args: dict of prioritized paperformat arguments.
        :param set_viewport_size: Enable a viewport sized '1024x1280' or '1280x1024' depending of landscape arg.
        :return: Content of the pdf as a string
        '''

        # Build the base command args for wkhtmltopdf bin
        command_args = self._build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size)

        files_command_args = []
        temporary_files = []
        if header:
            head_file_fd, head_file_path = tempfile.mkstemp(suffix='.html', prefix='report.header.tmp.')
            with closing(os.fdopen(head_file_fd, 'wb')) as head_file:
                head_file.write(header)
            temporary_files.append(head_file_path)
            files_command_args.extend(['--header-html', head_file_path])
        if footer:
            foot_file_fd, foot_file_path = tempfile.mkstemp(suffix='.html', prefix='report.footer.tmp.')
            with closing(os.fdopen(foot_file_fd, 'wb')) as foot_file:
                foot_file.write(footer)
            temporary_files.append(foot_file_path)
            files_command_args.extend(['--footer-html', foot_file_path])

        paths = []
        for i, body in enumerate(bodies):
            prefix = '%s%d.' % ('report.body.tmp.', i)
            body_file_fd, body_file_path = tempfile.mkstemp(suffix='.html', prefix=prefix)
            with closing(os.fdopen(body_file_fd, 'wb')) as body_file:
                body_file.write(body)
            paths.append(body_file_path)
            temporary_files.append(body_file_path)

        pdf_report_fd, pdf_report_path = tempfile.mkstemp(suffix='.pdf', prefix='report.tmp.')
        os.close(pdf_report_fd)
        temporary_files.append(pdf_report_path)

        try:
            wkhtmltopdf = [_get_wkhtmltopdf_bin()] + command_args + files_command_args + paths + [pdf_report_path]
            process = subprocess.Popen(wkhtmltopdf, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()

            if process.returncode not in [0, 1]:
                if process.returncode == -11:
                    message = _(
                        'Wkhtmltopdf failed (error code: %s). Memory limit too low or maximum file number of subprocess reached. Message : %s')
                else:
                    message = _('Wkhtmltopdf failed (error code: %s). Message: %s')
                raise UserError(message % (str(process.returncode), err[-1000:]))
        except:
            raise

        with open(pdf_report_path, 'rb') as pdf_document:
            pdf_content = pdf_document.read()

        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                _logger.error('Error when trying to remove file %s' % temporary_file)

        return pdf_content


class report_paperformat(models.Model):
    _name = "wantech.report.paperformat"
    _description = "Allows customization of a report."

    name = fields.Char('Name', required=True)
    default = fields.Boolean('Default paper format ?')
    format = fields.Selection([
        ('A0', 'A0  5   841 x 1189 mm'),
        ('A1', 'A1  6   594 x 841 mm'),
        ('A2', 'A2  7   420 x 594 mm'),
        ('A3', 'A3  8   297 x 420 mm'),
        ('A4', 'A4  0   210 x 297 mm, 8.26 x 11.69 inches'),
        ('A5', 'A5  9   148 x 210 mm'),
        ('A6', 'A6  10  105 x 148 mm'),
        ('A7', 'A7  11  74 x 105 mm'),
        ('A8', 'A8  12  52 x 74 mm'),
        ('A9', 'A9  13  37 x 52 mm'),
        ('B0', 'B0  14  1000 x 1414 mm'),
        ('B1', 'B1  15  707 x 1000 mm'),
        ('B2', 'B2  17  500 x 707 mm'),
        ('B3', 'B3  18  353 x 500 mm'),
        ('B4', 'B4  19  250 x 353 mm'),
        ('B5', 'B5  1   176 x 250 mm, 6.93 x 9.84 inches'),
        ('B6', 'B6  20  125 x 176 mm'),
        ('B7', 'B7  21  88 x 125 mm'),
        ('B8', 'B8  22  62 x 88 mm'),
        ('B9', 'B9  23  33 x 62 mm'),
        ('B10', ':B10    16  31 x 44 mm'),
        ('C5E', 'C5E 24  163 x 229 mm'),
        ('Comm10E', 'Comm10E 25  105 x 241 mm, U.S. '
         'Common 10 Envelope'),
        ('DLE', 'DLE 26 110 x 220 mm'),
        ('Executive', 'Executive 4   7.5 x 10 inches, '
         '190.5 x 254 mm'),
        ('Folio', 'Folio 27  210 x 330 mm'),
        ('Ledger', 'Ledger  28  431.8 x 279.4 mm'),
        ('Legal', 'Legal    3   8.5 x 14 inches, '
         '215.9 x 355.6 mm'),
        ('Letter', 'Letter 2 8.5 x 11 inches, '
         '215.9 x 279.4 mm'),
        ('Tabloid', 'Tabloid 29 279.4 x 431.8 mm'),
        ('custom', 'Custom')
        ], 'Paper size', default='A4', help="Select Proper Paper size")
    margin_top = fields.Float('Top Margin (mm)', default=40)
    margin_bottom = fields.Float('Bottom Margin (mm)', default=20)
    margin_left = fields.Float('Left Margin (mm)', default=7)
    margin_right = fields.Float('Right Margin (mm)', default=7)
    page_height = fields.Integer('Page height (mm)', default=False)
    page_width = fields.Integer('Page width (mm)', default=False)
    orientation = fields.Selection([
        ('Landscape', 'Landscape'),
        ('Portrait', 'Portrait')
        ], 'Orientation', default='Landscape')
    header_line = fields.Boolean('Display a header line', default=False)
    header_spacing = fields.Integer('Header spacing', default=35)
    dpi = fields.Integer('Output DPI', required=True, default=90)
    report_ids = fields.One2many('ir.actions.report', 'paperformat_id', 'Associated reports', help="Explicitly associated reports")

    @api.constrains('format')
    def _check_format_or_page(self):
        if self.filtered(lambda x: x.format != 'custom' and (x.page_width or x.page_height)):
            raise ValidationError(_('Error ! You cannot select a format AND specific page width/height.'))



# class AccountInvoiceItems(models.Model):
#     _inherit = "account.payment"
    #first_print = fields.Boolean(string="First Print", default=True)


# class AccountInvoiceItems3(models.Model):
#     _inherit = "account.invoice"
    
#     first_print = fields.Boolean(string="First Print", default=True)


class AccountMove(models.Model):
    _inherit = "account.move"
    name2 = fields.Char()

    # @api.depends('name')
    # def _name2(self):
    #     #temp_text = self.name
    #     #single_text =  temp_text.split('/', 1 )
    #     self.name2 = "sssssssss"


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    first_print = fields.Integer()
    payments_widget2_date = fields.Text(string='Payment Date',compute='_get_payments_vals2', groups="account.group_account_invoice")
    payments_widget2_ref = fields.Text(string='Payment Ref.')
    payment_move_line_ids = fields.Many2many('account.move.line', string='Payment Move Lines', compute='_compute_payments', store=True)
    money_extra = fields.Boolean(string="零用現金", default=False)
    #payments_widget_paid = fields.Text(compute='_get_payment_info_JSON2', groups="account.group_account_invoice")

    @api.one
    @api.depends('payment_move_line_ids.amount_residual')
    def _get_payment_info_JSON2(self):
        self.payments_widget_paid = json.dumps(False)
        if self.payment_move_line_ids:
           aaaa = self._get_payments_vals()
           for line in self.aaaa:
                move_vals = {
                    'amount': line.amount,
                }
                self.env['wantech.paymentswidgetpaid'].create(move_vals)


            


    @api.one
    @api.depends('payment_move_line_ids.amount_residual')
    def _get_payments_vals2(self):
        if not self.payment_move_line_ids:
            return []
        #if 'date' in payment_vals:
        if self.payment_move_line_ids:
            payment_vals = []
            payment_date = ''
            payment_ref = ''
            for payment in self.payment_move_line_ids:
                payment_date = payment.date
                payment_ref = payment.move_id.name
            
            self.payments_widget2_date = payment_date
            self.payments_widget2_ref = payment_ref
        
    # @api.one
    # @api.depends('move_id.line_ids.amount_residual')
    # def _compute_payments2(self):
    #     payment_lines = set()
    #     for line in self.move_id.line_ids:
    #         payment_lines.update(line.mapped('matched_credit_ids.credit_move_id.id'))
    #         payment_lines.update(line.mapped('matched_debit_ids.debit_move_id.id'))
    #     self.payment_move_line_ids = self.env['account.move.line'].browse(list(payment_lines))

    @api.multi
    def payment_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        self.first_print = self.first_print + 1
        #text = json.loads(self.payments_widget_paid)

        #logging.warning(self)

         #llowed_ids = set(self.env['account.account'].browse(ids).ids)

        logging.warning((self.move_name))
        logging.warning((self.payment_move_line_ids[0]['debit']))
        logging.warning((self.payment_move_line_ids[0]['credit']))
        logging.warning((self.payment_move_line_ids[0]['balance']))

        logging.warning((self.payment_move_line_ids[0]['company_currency_id']))
        logging.warning((self.payment_move_line_ids[0]['currency_id']))
        logging.warning((self.payment_move_line_ids[0]['amount_residual']))
        logging.warning((self.payment_move_line_ids[0]['amount_residual_currency']))
        logging.warning((self.payment_move_line_ids[0]['account_id']))
        logging.warning((self.payment_move_line_ids[0]['move_id']))
        logging.warning((self.payment_move_line_ids[0]['narration']))
        logging.warning((self.payment_move_line_ids[0]['ref']))
        logging.warning((self.payment_move_line_ids[0]['payment_id']))
        logging.warning((self.payment_move_line_ids[0]['statement_line_id']))

        logging.warning((self.payment_move_line_ids[0]['statement_id']))
        logging.warning((self.payment_move_line_ids[0]['reconciled']))
        logging.warning((self.payment_move_line_ids[0]['full_reconcile_id']))
        logging.warning((self.payment_move_line_ids[0]['matched_debit_ids']))
        logging.warning((self.payment_move_line_ids[0]['journal_id']))
        logging.warning((self.payment_move_line_ids[0]['analytic_line_ids']))
        logging.warning((self.payment_move_line_ids[0]['tax_ids']))
        logging.warning((self.payment_move_line_ids[0]['tax_line_id']))
        logging.warning((self.payment_move_line_ids[0]['analytic_account_id']))
        logging.warning((self.payment_move_line_ids[0]['analytic_tag_ids'])) 
        
        for aaa in self.payment_move_line_ids:
            for bbb in aaa.move_id:
                temp_text = bbb.name
                single_text =  temp_text.split('/', 1 )
                logging.warning(single_text[0]) 
                bbb.name2 =single_text[0]
        #aaa = json.dumps(self.payment_move_line_ids[0][''])
        
        #logging.warning(aaa)
        return self.env.ref('customer_elderly.report_pdf3').report_action(self)
        
    @api.model
    def create(self, vals):
        onchanges = {
            '_onchange_partner_id': ['account_id', 'payment_term_id', 'fiscal_position_id', 'partner_bank_id'],
            '_onchange_journal_id': ['currency_id'],
        }
        #logging.warning(vals)
        if vals['origin'] == False:
            if 'invoice_line_ids' in vals:
                foundItem = False
                for item in vals['invoice_line_ids']:
                    if foundItem is False:
                        if 'name' in item[2]:
                            if vals['comment'] == False:
                                vals['comment'] = vals['invoice_line_ids'][0][2]['name']
                                foundItem= True
        
        for onchange_method, changed_fields in onchanges.items():
            if any(f not in vals for f in changed_fields):
                invoice = self.new(vals)
                getattr(invoice, onchange_method)()
                for field in changed_fields:
                    if field not in vals and invoice[field]:
                        vals[field] = invoice._fields[field].convert_to_write(invoice[field], invoice)
        if not vals.get('account_id',False):
            raise UserError(_('Configuration error!\nCould not find any account to create the invoice, are you sure you have a chart of account installed?'))

        invoice = super(AccountInvoice, self.with_context(mail_create_nolog=True)).create(vals)

        if any(line.invoice_line_tax_ids for line in invoice.invoice_line_ids) and not invoice.tax_line_ids:
            invoice.compute_taxes()
        return invoice

    @api.multi
    def _write(self, vals):
        pre_not_reconciled = self.filtered(lambda invoice: not invoice.reconciled)
        pre_reconciled = self - pre_not_reconciled
        #logging.warning(vals)
        #logging.warning(self["origin"])
        
        #logging.warning('_write')
        if self["origin"] == False:
            if 'invoice_line_ids' in vals:
                currentDesc =''
                checkDone = True
                if len(vals['invoice_line_ids']) > 0:
                    for invoicecustom in vals['invoice_line_ids']:
                        if checkDone :
                            if invoicecustom[0] == 0:
                                if invoicecustom[2]['name']:
                                    currentDesc = invoicecustom[2]['name']
                                    checkDone = False
                                    break
                            elif invoicecustom[0] == 1:
                                if 'name' in invoicecustom[2]:
                                    currentDesc = invoicecustom[2]['name']
                                    checkDone = False
                                    break
                                else:
                                    company = self.env['account.invoice.line'].browse(invoicecustom[1])
                                    currentDesc = company.name
                                    checkDone = False
                                    break
                    vals['comment'] = currentDesc
        res = super(AccountInvoice, self)._write(vals)
        reconciled = self.filtered(lambda invoice: invoice.reconciled)
        not_reconciled = self - reconciled
        (reconciled & pre_reconciled).filtered(lambda invoice: invoice.state == 'open').action_invoice_paid()
        (not_reconciled & pre_not_reconciled).filtered(lambda invoice: invoice.state == 'paid').action_invoice_re_open()
        return res

    @api.one
    @api.depends('payment_move_line_ids.amount_residual')
    def _get_payment_info_JSON(self):

        self.payments_widget = json.dumps(False)
        if self.payment_move_line_ids:
            info = {'title': _('Less Payment'), 'outstanding': False, 'content': self._get_payments_vals()}
            self.payments_widget = json.dumps(info)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    first_print = fields.Integer()
    first_print_book = fields.Integer()
    first_print_deposit = fields.Integer()
    exp_date = fields.Date(string='到期日期', default=fields.Date.context_today, required=True, copy=False)
    check_to_print = fields.Integer(string='check_to_print', default=1, required=True, copy=False)

    @api.multi
    def payment_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        self.first_print = self.first_print + 1
        for invoice_ids in self.invoice_ids:
            for move_id in invoice_ids.payment_move_line_ids:
                for bbb in move_id.move_id:
                    temp_text = bbb.name
                    single_text =  temp_text.split('/', 1 )
                    logging.warning(bbb.name2)
                    #bbb.name2 =single_text[0]




        return self.env.ref('account.action_report_payment_receipt').report_action(self)

    @api.multi
    def payment_print_book(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        self.first_print_book = self.first_print_book + 1
        logging.warning(self)
        return self.env.ref('customer_elderly.wantech_payment_receipt_book_call').report_action(self)

    @api.multi
    def payment_print_deposit(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        self.first_print_deposit = self.first_print_deposit + 1
        logging.warning(self)
        return self.env.ref('customer_elderly.wantech_payment_receipt_deposit_call').report_action(self)


    @api.multi
    def payment_print_cheque(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        self.first_print = self.first_print + 1
        # #self.write({'first_print': False})
        self.form_type=1
        return self.env.ref('dev_print_cheque.action_report_print_cheque').report_action(self)



    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            if not rec.name and rec.payment_type != 'transfer':
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})
            if rec.check_to_print == 2:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Warning : Customer is about or exceeded their credit limit',
                    'res_model': 'account.payment',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id'    : self.id,
                    'view_id': self.env.ref('account.view_account_payment_form').id,
                    'target': 'current',
                }
                


class SaleSubscription2(models.Model):
    _inherit = "sale.subscription"

    recurring_date_smaller_next_date = fields.Integer()


    @api.multi
    def _recurring_create_invoice(self, automatic=False):
        auto_commit = self.env.context.get('auto_commit', True)
        cr = self.env.cr
        invoices = self.env['account.invoice']
        current_date = time.strftime('%Y-%m-%d')
        imd_res = self.env['ir.model.data']
        template_res = self.env['mail.template']
        if len(self) > 0:
            subscriptions = self
        else:
            domain = [('recurring_next_date', '<=', current_date),
                      ('state', 'in', ['open', 'pending'])]
            subscriptions = self.search(domain)
        if subscriptions:
            sub_data = subscriptions.read(fields=['id', 'company_id'])
            for company_id in set(data['company_id'][0] for data in sub_data):
                sub_ids = [s['id'] for s in sub_data if s['company_id'][0] == company_id]
                subs = self.with_context(company_id=company_id, force_company=company_id).browse(sub_ids)
                context_company = dict(self.env.context, company_id=company_id, force_company=company_id)
                for subscription in subs:
                    if automatic and auto_commit:
                        cr.commit()
                    # payment + invoice (only by cron)
                    if subscription.template_id.payment_mandatory and subscription.recurring_total and automatic:
                        try:
                            payment_token = subscription.payment_token_id
                            if payment_token:
                                invoice_values = subscription.with_context(lang=subscription.partner_id.lang)._prepare_invoice()
                                new_invoice = self.env['account.invoice'].with_context(context_company).create(invoice_values)
                                new_invoice.message_post_with_view('mail.message_origin_link',
                                    values = {'self': new_invoice, 'origin': subscription},
                                    subtype_id = self.env.ref('mail.mt_note').id)
                                new_invoice.with_context(context_company).compute_taxes()
                                tx = subscription._do_payment(payment_token, new_invoice, two_steps_sec=False)[0]
                                # commit change as soon as we try the payment so we have a trace somewhere
                                if auto_commit:
                                    cr.commit()
                                if tx.state in ['done', 'authorized']:
                                    subscription.send_success_mail(tx, new_invoice)
                                    msg_body = 'Automatic payment succeeded. Payment reference: <a href=# data-oe-model=payment.transaction data-oe-id=%d>%s</a>; Amount: %s. Invoice <a href=# data-oe-model=account.invoice data-oe-id=%d>View Invoice</a>.' % (tx.id, tx.reference, tx.amount, new_invoice.id)
                                    subscription.message_post(body=msg_body)
                                    if auto_commit:
                                        cr.commit()
                                else:
                                    _logger.error('Fail to create recurring invoice for subscription %s', subscription.code)
                                    if auto_commit:
                                        cr.rollback()
                                    new_invoice.unlink()
                            amount = subscription.recurring_total
                            date_close = datetime.strptime(subscription.recurring_next_date, "%Y-%m-%d") + relativedelta(days=15)
                            close_subscription = current_date >= date_close.strftime('%Y-%m-%d')
                            logging.warning(current_date-date_close)
                            email_context = self.env.context.copy()
                            email_context.update({
                                'payment_token': subscription.payment_token_id and subscription.payment_token_id.name,
                                'renewed': False,
                                'total_amount': amount,
                                'email_to': subscription.partner_id.email,
                                'code': subscription.code,
                                'currency': subscription.pricelist_id.currency_id.name,
                                'date_end': subscription.date,
                                'date_close': date_close.date()
                            })
                            if close_subscription:
                                _, template_id = imd_res.get_object_reference('sale_subscription', 'email_payment_close')
                                template = template_res.browse(template_id)
                                template.with_context(email_context).send_mail(subscription.id)
                                _logger.debug("Sending Subscription Closure Mail to %s for subscription %s and closing subscription", subscription.partner_id.email, subscription.id)
                                msg_body = 'Automatic payment failed after multiple attempts. Subscription closed automatically.'
                                subscription.message_post(body=msg_body)
                            else:
                                _, template_id = imd_res.get_object_reference('sale_subscription', 'email_payment_reminder')
                                msg_body = 'Automatic payment failed. Subscription set to "To Renew".'
                                if (datetime.today() - datetime.strptime(subscription.recurring_next_date, '%Y-%m-%d')).days in [0, 3, 7, 14]:
                                    template = template_res.browse(template_id)
                                    template.with_context(email_context).send_mail(subscription.id)
                                    _logger.debug("Sending Payment Failure Mail to %s for subscription %s and setting subscription to pending", subscription.partner_id.email, subscription.id)
                                    msg_body += ' E-mail sent to customer.'
                                subscription.message_post(body=msg_body)
                            subscription.write({'state': 'close' if close_subscription else 'pending'})
                            if auto_commit:
                                cr.commit()
                        except Exception:
                            if auto_commit:
                                cr.rollback()
                            # we assume that the payment is run only once a day
                            last_tx = self.env['payment.transaction'].search([('reference', 'like', 'SUBSCRIPTION-%s-%s' % (subscription.id, datetime.date.today().strftime('%y%m%d')))], limit=1)
                            error_message = "Error during renewal of subscription %s (%s)" % (subscription.code, 'Payment recorded: %s' % last_tx.reference if last_tx and last_tx.state == 'done' else 'No payment recorded.')
                            traceback_message = traceback.format_exc()
                            _logger.error(error_message)
                            _logger.error(traceback_message)

                    # invoice only
                    else:
                        try:
                            invoice_values = subscription.with_context(lang=subscription.partner_id.lang)._prepare_invoice()
                            new_invoice = self.env['account.invoice'].with_context(context_company).create(invoice_values)
                            new_invoice.message_post_with_view('mail.message_origin_link',
                                values = {'self': new_invoice, 'origin': subscription},
                                subtype_id = self.env.ref('mail.mt_note').id)
                            new_invoice.with_context(context_company).compute_taxes()
                            invoices += new_invoice
                            next_date = datetime.strptime(subscription.recurring_next_date or current_date, "%Y-%m-%d")
                            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
                            invoicing_period = relativedelta(**{periods[subscription.recurring_rule_type]: subscription.recurring_interval})
                            new_date = next_date + invoicing_period

                            oldDate = datetime.strptime(subscription.recurring_next_date, '%Y-%m-%d')
                            curDate = datetime.strptime(current_date, '%Y-%m-%d')
                            if oldDate < curDate:

                                date_start = datetime.strptime(subscription.date_start, "%Y-%m-%d")
                                date_start_year = date_start.year
                                date_start_month = date_start.month
                                date_start_day = 1

                                #get first day and days of month
                                firstDayWeekDay, monthRange = calendar.monthrange(date_start_year, date_start_month)

                                #days of month - start days
                                date_range_price_rate = monthRange - date_start.day + 1
                                logging.warning(date_range_price_rate)

                                # add 1 month into new date
                                new_date = oldDate + invoicing_period

                                #print(oldDate)
                                for sss in invoices.invoice_line_ids:
                                    sss.price_unit = sss.price_unit * (date_range_price_rate/monthRange)
                                    #invoices.amount_total = sss.price_unit * (date_range_price_rate/monthRange)
                                lastdate = datetime(date_start_year, date_start_month, monthRange, 0, 0)
                                invoices.comment = "%s/%s/%s - %s/%s/%s" %(date_start_year,date_start_month,date_start.day,date_start_year,date_start_month,monthRange)

                            subscription.write({'recurring_next_date': new_date.strftime('%Y-%m-%d')})
                            if automatic and auto_commit:
                                cr.commit()
                        except Exception:
                            if automatic and auto_commit:
                                cr.rollback()
                                _logger.exception('Fail to create recurring invoice for subscription %s', subscription.code)
                            else:
                                raise
            #logging.warning(invoices.invoice_line_ids)
        return invoices

    # def action_subscription_invoice(self):
    #     self.ensure_one()
    #     invoices = self.env['account.invoice'].search([('invoice_line_ids.subscription_id', 'in', self.ids)])
    #     action = self.env.ref('account.action_invoice_tree1').read()[0]
    #     action["context"] = {"create": False}
    #     if len(invoices) > 1:
    #         action['domain'] = [('id', 'in', invoices.ids)]
    #     elif len(invoices) == 1:
    #         action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
    #         action['res_id'] = invoices.ids[0]
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #     logging.warning(invoices.invoice_line_ids)
    #     return action

    @api.depends('recurring_invoice_line_ids', 'recurring_invoice_line_ids.quantity', 'recurring_invoice_line_ids.price_subtotal')
    def _compute_recurring_total(self):
        for account in self:
            account.recurring_total = sum(line.price_subtotal for line in account.recurring_invoice_line_ids)

    def _prepare_invoice_data(self):
        self.ensure_one()

        if not self.partner_id:
            raise UserError(_("You must first select a Customer for Subscription %s!") % self.name)

        if 'force_company' in self.env.context:
            company = self.env['res.company'].browse(self.env.context['force_company'])
        else:
            company = self.company_id
            self = self.with_context(force_company=company.id, company_id=company.id)

        fpos_id = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id)
        journal = self.template_id.journal_id or self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', company.id)], limit=1)
        if not journal:
            raise UserError(_('Please define a sale journal for the company "%s".') % (company.name or '', ))

        next_date = fields.Date.from_string(self.recurring_next_date)
        if not next_date:
            raise UserError(_('Please define Date of Next Invoice of "%s".') % (self.display_name,))
        periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        end_date = next_date + relativedelta(**{periods[self.recurring_rule_type]: self.recurring_interval})
        end_date = end_date - relativedelta(days=1)     # remove 1 day as normal people thinks in term of inclusive ranges.
        addr = self.partner_id.address_get(['delivery'])

        return {
            'account_id': self.partner_id.property_account_receivable_id.id,
            'type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'partner_shipping_id': addr['delivery'],
            'currency_id': self.pricelist_id.currency_id.id,
            'journal_id': journal.id,
            'origin': self.code,
            'fiscal_position_id': fpos_id,
            'payment_term_id': self.partner_id.property_payment_term_id.id,
            'company_id': company.id,
            'comment': _("%s - %s") % (format_date(self.env, next_date), format_date(self.env, end_date)),
            'user_id': self.user_id.id,
        }

    def prepare_invoice_data(self):
            self.ensure_one()

            if not self.partner_id:
                raise UserError(_("You must first select a Customer for Subscription %s!") % self.name)

            if 'force_company' in self.env.context:
                company = self.env['res.company'].browse(self.env.context['force_company'])
            else:
                company = self.company_id
                self = self.with_context(force_company=company.id, company_id=company.id)

            fpos_id = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id)
            journal = self.template_id.journal_id or self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', company.id)], limit=1)
            if not journal:
                raise UserError(_('Please define a sale journal for the company "%s".') % (company.name or '', ))

            next_date = fields.Date.from_string(self.recurring_next_date)
            if not next_date:
                raise UserError(_('Please define Date of Next Invoice of "%s".') % (self.display_name,))
            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
            end_date = next_date + relativedelta(**{periods[self.recurring_rule_type]: self.recurring_interval})
            end_date = end_date - relativedelta(days=1)     # remove 1 day as normal people thinks in term of inclusive ranges.
            addr = self.partner_id.address_get(['delivery'])

            return {
                'account_id': self.partner_id.property_account_receivable_id.id,
                'type': 'out_invoice',
                'partner_id': self.partner_id.id,
                'partner_shipping_id': addr['delivery'],
                'currency_id': self.pricelist_id.currency_id.id,
                'journal_id': journal.id,
                'origin': self.code,
                'fiscal_position_id': fpos_id,
                'payment_term_id': self.partner_id.property_payment_term_id.id,
                'company_id': company.id,
                'comment': _("%s - %s") % (format_date(self.env, next_date), format_date(self.env, end_date)),
                'user_id': self.user_id.id,
            }
        


# class AccountInvoiceItems2(models.Model):
#     _inherit = "res.partner"

    #invoice_ids_product = fields.One2many('account.invoice.line', 'number', readonly=True, copy=False, ondelete='restrict')
    #print(invoice_ids_product)
    #invoice_ids_product = fields.Many2many('account.invoice','account.invoice.line', 'invoice_id', string="Invoices", copy=False, readonly=True)
    #account_idaaaa = fields.Many2one('account.invoice', string='Account', readonly=True, domain=[('id', '=', 8)])
    #account_invoice_line_lists= fields.Many2one('account.invoice.line', domain=[('id', '=', 8)])
    #account_invoice_line_lists = fields.One2many('account.invoice','account.invoice.line',string='Taxes', domain=[('invoice_id','=',8)])
    #account_invoice_line_lists = fields.One2many('account.invoice', 'account.invoice.', readonly=True, copy=False, ondelete='restrict')
    # @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    # def _compute_payment_difference2(self):
    #     self.account_invoice_line_lists = self.env['account.invoice.line'].search([('invoice_id', '=', 8)])


    #     return "aaa"

    #payment_difference2 = fields.Char(compute='_compute_payment_difference2', readonly=True)

        # invoicelines2 = self.env['account.invoice.line'].search([('invoice_id', '=', 8)])

        # for inv_line2 in invoicelines2:

    
