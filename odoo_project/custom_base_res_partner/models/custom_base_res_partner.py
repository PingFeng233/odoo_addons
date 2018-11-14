# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class custom_base_res_partner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    name = fields.Char(index=True, translate=True)

    custom_customer_number = fields.Char(string='Customer No', required=True, index=True, copy=False,
                                         default=lambda self: _('New'))
    custom_region = fields.Many2one('custom_region', string='Region')
    custom_type = fields.Many2one('custom_type', string='Type')
    custom_qty_control = fields.Many2one('custom_qty_control', string='Qty Control')
    custom_in_charge = fields.Many2one('hr.employee', string='In-Charge')

    # custom_name_chi = fields.Char(string='Name(chi)')

    custom_days = fields.Float(digits=(12, 1), string='Days')
    custom_business_type = fields.Many2one('custom_business_type', string='Business Type')
    custom_short_name = fields.Char(string='Short Name')
    custom_trade_terms = fields.Many2one('custom_trade_terms', string='Trade Terms')
    custom_trade_port = fields.Many2one('custom_trade_port', string='Trade Port')
    custom_status = fields.Many2one('custom_status', string='Status')
    custom_customer_status = fields.Many2one('custom_customer_status', string='Customer Status')
    custom_commission = fields.Float(digits=(3, 2), string='Commission%')
    custom_remark = fields.Text(string='Remark')
    custom_vendor_status = fields.Many2one('custom_vendor_status', string='Vendor Status')

    is_company = fields.Boolean(string='Is a Company', default=True,
                                help="Check if the contact is a company, otherwise it is a person")
    custom_control_number = fields.Char("Control No.")

    @api.model
    def create(self, vals):
        if vals.get('custom_customer_number', _('New')) == _('New'):
            if vals.get('customer', None) == False and vals.get('supplier', None) == True:
                vals['custom_customer_number'] = self.env['ir.sequence'].next_by_code('res.partner.vendor') or _(
                    'New')
            else:
                vals['custom_customer_number'] = self.env['ir.sequence'].next_by_code('res.partner.customer') or _(
                    'New')
            return super(custom_base_res_partner, self).create(vals)

    @api.constrains('custom_days', 'custom_commission')
    def _check_something(self):
        for record in self:
            if record.custom_days < 0:
                raise exceptions.ValidationError("Incorrect 'Days' value: %s" % record.custom_days)
            if record.custom_commission < 0:
                raise exceptions.ValidationError("Incorrect 'Commission' value: %s" % record.custom_commission)
            if record.custom_commission > 100:
                raise exceptions.ValidationError("Incorrect 'Commission' value: %s" % record.custom_commission)


class custom_region(models.Model):
    _name = 'custom_region'
    name = fields.Char()


class custom_type(models.Model):
    _name = 'custom_type'
    name = fields.Char()


class custom_qty_control(models.Model):
    _name = 'custom_qty_control'
    name = fields.Char()


class custom_business_type(models.Model):
    _name = 'custom_business_type'
    name = fields.Char()


class custom_trade_terms(models.Model):
    _name = 'custom_trade_terms'
    name = fields.Char()


class custom_trade_port(models.Model):
    _name = 'custom_trade_port'
    name = fields.Char()


class custom_status(models.Model):
    _name = 'custom_status'
    name = fields.Char()


class custom_customer_status(models.Model):
    _name = 'custom_customer_status'
    name = fields.Char()


class custom_vendor_status(models.Model):
    _name = 'custom_vendor_status'
    name = fields.Char()
