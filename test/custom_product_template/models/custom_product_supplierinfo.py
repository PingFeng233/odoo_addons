# coding:utf-8
import logging

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.osv.osv import osv


class Custom_product_supplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    #   Purchase
    buik_lead_time = fields.Float('Buik Lead Time', digits=(12, 2), required=True)
    sample_lead_time = fields.Float('Sample Lead Time', digits=(12, 2))
    wastage = fields.Float('Wastage', digits=(12, 2))
    test_result = fields.Many2one('custom_test_result', 'Test Result')
    season = fields.Many2one('custom_season', string='Season')
    sample_max_order = fields.Float('Sample Max Order', digits=(12, 2))
    sample_min_order = fields.Float('Sample Min Order', digits=(12, 2))
    bulk_max_order = fields.Float('Bulk Max Order', digits=(12, 2))
    bulk_min_order = fields.Float('Bulk Min Order', digits=(12, 2))
    remark = fields.Text('Remark')

    @api.onchange('buik_lead_time', 'sample_lead_time', 'wastage', 'sample_max_order',
                  'sample_min_order', 'bulk_max_order', 'bulk_min_order')
    def _check_onchange(self):
        for record in self:
            if record.buik_lead_time < 0:
                raise osv.except_osv((u'警告!'), (u'buik_lead_time不能小于0.'))
                # raise ValidationError('buik_lead_time不能小于0')
            if record.sample_lead_time < 0:
                raise ValidationError('sample_lead_time不能小于0')
            if record.wastage < 0:
                raise ValidationError('wastage不能小于0')
            if record.sample_max_order < 0:
                raise ValidationError('sample_max_order不能小于0')
            if record.sample_min_order < 0:
                raise ValidationError('sample_min_order不能小于0')
            if record.bulk_max_order < 0:
                raise ValidationError('bulk_max_order不能小于0')
            if record.bulk_min_order < 0:
                raise ValidationError('bulk_min_order不能小于0')

    @api.constrains('buik_lead_time', 'sample_lead_time', 'wastage', 'sample_max_order',
                    'sample_min_order', 'bulk_max_order', 'bulk_min_order')
    def _check_float_field(self):
        for record in self:
            if record.buik_lead_time < 0:
                raise ValidationError('buik_lead_time不能小于0')
            if record.sample_lead_time < 0:
                raise ValidationError('sample_lead_time不能小于0')
            if record.wastage < 0:
                raise ValidationError('wastage不能小于0')
            if record.sample_max_order < 0:
                raise ValidationError('sample_max_order不能小于0')
            if record.sample_min_order < 0:
                raise ValidationError('sample_min_order不能小于0')
            if record.bulk_max_order < 0:
                raise ValidationError('bulk_max_order不能小于0')
            if record.bulk_min_order < 0:
                raise ValidationError('bulk_min_order不能小于0')


class Custom_test_result(models.Model):
    _name = 'custom_test_result'
    name = fields.Char()
