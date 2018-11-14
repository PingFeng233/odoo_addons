# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Custom_discount(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    grou = fields.Many2one('custom_group', string='Group')


class Custom_group(models.Model):
    _name = 'custom_group'

    name = fields.Char('Group')
    discount = fields.Float(digits=(4, 2), string='Discount(%)')


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    @api.onchange('order_line')
    def _change_discount(self):
        if self.order_line and not self._origin:
            line = self.order_line[-1]
            print(line.discount)
            if line['discount'] == 0.0:
                values = {'discount': self.partner_id.grou.discount}
                line.update(values)
    # 订单行保存之后,discount才能修改为0


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"

    @api.onchange('invoice_line_ids')
    def _change_discount(self):
        if self.invoice_line_ids and not self._origin:
            line = self.invoice_line_ids[-1]
            if line['discount'] == 0.0:
                line['discount'] = self.partner_id.grou.discount
