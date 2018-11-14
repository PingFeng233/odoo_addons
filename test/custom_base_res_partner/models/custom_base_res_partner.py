# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class Custom_base_res_partner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'
    name = fields.Char(index=True,translate=True)
    custom_payment = fields.Many2one('custom_payment', string='Payment')
    custom_region = fields.Many2one('custom_region', string='Region')
    custom_type = fields.Many2one('custom_type', string='Type')
    custom_qty_control = fields.Many2one('custom_qty_control', string='Qty Control')
    custom_in_charge = fields.Many2one('hr.employee', string='In-Charge')
    custom_currency = fields.Many2one('custom_currency', string='Currency')
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
    vendor_status = fields.Many2one('vendor_status', string='Vendor_Status')
    custom_number = fields.Char('Customer No:', copy=False, default='New')
    is_company = fields.Boolean(string='Is a Company', default=True,
                                help="Check if the contact is a company, otherwise it is a person")

    @api.model
    def create(self, vals):
        if vals.get('custom_number', 'New') == 'New':
            vals['custom_number'] = self.env['ir.sequence'].next_by_code('ABC')
            return super(Custom_base_res_partner, self).create(vals)

    @api.constrains('custom_days', 'custom_commission')
    def _check_something(self):
        for record in self:
            if record.custom_days < 0:
                raise exceptions.ValidationError("Incorrect 'Days' value: %s" % record.custom_days)
            if record.custom_commission < 0:
                raise exceptions.ValidationError("Incorrect 'Commission' value: %s" % record.custom_commission)
            if record.custom_commission > 100:
                raise exceptions.ValidationError("Incorrect 'Commission' value: %s" % record.custom_commission)


class custom_payment(models.Model):
    _name = 'custom_payment'
    name = fields.Char()


class custom_region(models.Model):
    _name = 'custom_region'
    name = fields.Char()


class custom_type(models.Model):
    _name = 'custom_type'
    name = fields.Char()


class custom_qty_control(models.Model):
    _name = 'custom_qty_control'
    name = fields.Char()


class custom_currency(models.Model):
    _name = 'custom_currency'
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


class vendor_status(models.Model):
    _name = 'vendor_status'
    name = fields.Char()
