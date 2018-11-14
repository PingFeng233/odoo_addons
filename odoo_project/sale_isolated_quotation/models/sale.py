# -*- coding: utf-8 -*-
# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_order = fields.Boolean(
        string='Is Order',
        readonly=True,
        index=True,
        default=lambda self: self._context.get('is_order', False),
    )
    quote_id = fields.Many2one(
        'sale.order',
        string='Quotation Reference',
        readonly=True,
        ondelete='restrict',
        copy=False,
        help="For Sales Order, this field references to its Quotation",
    )
    order_id = fields.Many2one(
        'sale.order',
        string='Order Reference',
        readonly=True,
        ondelete='restrict',
        copy=False,
        help="For Quotation, this field references to its Sales Order",
    )
    state2 = fields.Selection(
        [('draft', 'Draft'),
         ('sent', 'Mail Sent'),
         ('cancel', 'Cancelled'),
         ('done', 'Done'), ],
        string='Status',
        readonly=True,
        related='state',
        help="A dummy state used for quotation",
    )
    quotelist = fields.Many2many('quotelist', 'sale_order_quotelist_rel', 'order_id', 'quote_id',
                                 domain=[('name', '!=', None)])

    @api.model
    def create(self, vals):
        is_order = vals.get('is_order', False) or \
                   self._context.get('is_order', False)
        if not is_order and vals.get('name', '/') == '/':
            Seq = self.env['ir.sequence']
            vals['name'] = Seq.next_by_code('sale.quotation') or '/'
        active = True
        record = super(SaleOrder, self).create(vals)
        if record.is_order == True:
            active = False
        self.env['quotelist'].create({'order_id': record.ids,
                                      'name': record.id,
                                      'active': active})
        return record

    @api.multi
    def action_convert_to_order(self):
        self.ensure_one()
        if self.is_order:
            raise UserError(
                _('Only quotation can convert to order'))
        Seq = self.env['ir.sequence']
        order = self.copy({
            'name': Seq.next_by_code('sale.order') or '/',
            'is_order': True,
            'quote_id': self.id,
            'client_order_ref': self.client_order_ref,
        })
        self.order_id = order.id  # Reference from this quotation to order
        if self.state == 'draft':
            self.action_done()
        return self.open_sale_order()

    @api.model
    def open_sale_order(self):
        return {
            'name': _('Sales Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'sale.order',
            'context': {'is_order': True, },
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': "[('is_order', '=', True)]",
            'res_id': self.order_id and self.order_id.id or False,
        }

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        order_lines = self.env['sale.order.line'].search([('order_id', '=', self.id)])
        for line in order_lines:
            product = self.env['product.product'].search(
                [('id', '=', line.product_id.id)])[0]
            product_variants = self.env['product.product'].search_count([(
                'product_tmpl_id.id', '=', product.product_tmpl_id.id)])
            if (product_variants > 1 and not product.attribute_value_ids) or (
                    product_variants == 1 and product.product_tmpl_id.has_variants):
                raise UserError('请检查销售订单信息')
        super(SaleOrder, self).action_confirm()

    @api.multi
    def action_quote_list(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'view_type': 'form',
            'name': u'报价单',
            'target': "new",
            'res_id': self.id,
            'view_id': self.env.ref('sale_isolated_quotation.quotelist_form').id,
        }

    @api.multi
    def action_add_order(self):
        self.ensure_one()
        order_lines = self.env['sale.order.line'].search(
            [('order_id', 'in', [quote.name.id for quote in self.quotelist])])
        for line in order_lines:
            new_line = line.copy({'order_id': self.id})
            self.order_line += new_line


class QuoteList(models.Model):
    _name = 'quotelist'

    name = fields.Many2one('sale.order', readonly=True)
    order_id = fields.Many2many('sale.order', 'sale_order_quotelist_rel', 'quote_id', 'order_id')
    active = fields.Boolean(default=True)
