# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class custom_product(models.Model):
    _inherit = 'product.template'
    _name = 'product.template'

    name = fields.Char(index=True, translate=True)
    # -> General Information
    custom_is_materia = fields.Boolean(default=False, string='Is Materia')
    custom_is_product = fields.Boolean(default=False, string='Is Product')
    # by common
    # custom_name_in_chi = fields.Char(string='Name in Chi')
    # custom_description_in_chi = fields.Text(string='Description in Chi')
    custom_short_description = fields.Char(string='Short Description', translate=True)
    # custom_description_in_eng = fields.Text(string='Description in Eng')
    custom_description = fields.Text(string='Description', translate=True)

    # by product
    custom_paper_no = fields.Char(string='Paper No.')
    custom_brand = fields.Many2one('custom_brand', string='Brand')
    custom_season = fields.Many2one('custom_season', string='Season')

    # by materia
    custom_in_charge = fields.Many2one('hr.employee', string='In-Charge')
    custom_material_type = fields.Many2one('custom_material_type', string='Material Type')
    custom_ingredient = fields.Many2one('custom_ingredient', string='Ingredient(成份)')
    custom_weight = fields.Float(digits=(12, 2), string='Weight')
    custom_region = fields.Many2one('custom_region', string='Region(地區)')
    custom_remark = fields.Text(string='Remark')
    custom_status = fields.Many2one('custom_status', string='Status')
    custom_user_status = fields.Many2one('custom_user_status', string='User Status')
    custom_method = fields.Many2one('custom_method', string='Method')
    custom_tissue_yarn_count = fields.Many2one('custom_tissue_yarn_count', string='組織/紗支數')
    custom_postprocessing1 = fields.Char(string='後處理1')
    custom_postprocessing2 = fields.Char(string='後處理2')

    @api.constrains('custom_weight')
    def _check_something(self):
        for record in self:
            if record.custom_weight < 0:
                raise exceptions.ValidationError("Incorrect 'Weight' value: %s" % record.custom_weight)


class custom_region(models.Model):
    _name = 'custom_region'
    name = fields.Char()


class custom_brand(models.Model):
    _name = 'custom_brand'
    name = fields.Char()


class custom_season(models.Model):
    _name = 'custom_season'
    name = fields.Char()


class custom_material_type(models.Model):
    _name = 'custom_material_type'
    name = fields.Char()


class custom_ingredient(models.Model):
    _name = 'custom_ingredient'
    name = fields.Char()


class custom_status(models.Model):
    _name = 'custom_status'
    name = fields.Char()


class custom_user_status(models.Model):
    _name = 'custom_user_status'
    name = fields.Char()


class custom_method(models.Model):
    _name = 'custom_method'
    name = fields.Char()


class custom_tissue_yarn_count(models.Model):
    _name = 'custom_tissue_yarn_count'
    name = fields.Char()


class custom_product_supplierinfo(models.Model):
    _inherit = 'product.supplierinfo'
    _name = 'product.supplierinfo'

    custom_season = fields.Many2one('custom_season', string='Season')
    custom_remark = fields.Text(string='Remark')
    custom_test_result = fields.Many2one('custom_test_result', string='Test Result')
    custom_buik_lead_time = fields.Float(digits=(12, 2), string='Buik Lead Time')
    custom_wastage = fields.Float(digits=(12, 2), string='Wastage')
    custom_bulk_max_order = fields.Float(digits=(12, 2), string='Bulk Max Order')
    custom_bulk_min_order = fields.Float(digits=(12, 2), string='Bulk Min Order')
    custom_sample_lead_time = fields.Float(digits=(12, 2), string='Sample Lead Time')
    custom_sample_max_order = fields.Float(digits=(12, 2), string='Sample Max Order')
    custom_sample_min_order = fields.Float(digits=(12, 2), string='Sample Min Order')

    @api.constrains('custom_buik_lead_time', 'custom_wastage', 'custom_bulk_max_order', 'custom_bulk_min_order',
                    'custom_sample_lead_time', 'custom_sample_max_order', 'custom_sample_min_order')
    def _check_supplierinfo(self):
        for record in self:
            if record.custom_buik_lead_time < 0:
                raise exceptions.ValidationError("Incorrect 'Buik Lead Time' value: %s" % record.custom_buik_lead_time)
            if record.custom_wastage < 0:
                raise exceptions.ValidationError("Incorrect 'Wastage' value: %s" % record.custom_wastage)
            if record.custom_bulk_max_order < 0:
                raise exceptions.ValidationError("Incorrect 'Bulk Max Order' value: %s" % record.custom_bulk_max_order)
            if record.custom_bulk_min_order < 0:
                raise exceptions.ValidationError("Incorrect 'Bulk Min Order' value: %s" % record.custom_bulk_min_order)
            if record.custom_sample_lead_time < 0:
                raise exceptions.ValidationError(
                    "Incorrect 'Sample Lead Time' value: %s" % record.custom_sample_lead_time)
            if record.custom_sample_max_order < 0:
                raise exceptions.ValidationError(
                    "Incorrect 'Sample Max Order' value: %s" % record.custom_sample_max_order)
            if record.custom_sample_min_order < 0:
                raise exceptions.ValidationError(
                    "Incorrect 'Sample Min Order' value: %s" % record.custom_sample_min_order)

    @api.onchange('custom_buik_lead_time', 'custom_wastage', 'custom_bulk_max_order', 'custom_bulk_min_order',
                  'custom_sample_lead_time', 'custom_sample_max_order', 'custom_sample_min_order')
    def _check_supplierinfo_from(self):
        for record in self:
            if record.custom_buik_lead_time < 0:
                raise exceptions.ValidationError("Incorrect 'Buik Lead Time' value: %s" % record.custom_buik_lead_time)
            if record.custom_wastage < 0:
                raise exceptions.ValidationError("Incorrect 'Wastage' value: %s" % record.custom_wastage)
            if record.custom_bulk_max_order < 0:
                raise exceptions.ValidationError("Incorrect 'Bulk Max Order' value: %s" % record.custom_bulk_max_order)
            if record.custom_bulk_min_order < 0:
                raise exceptions.ValidationError("Incorrect 'Bulk Min Order' value: %s" % record.custom_bulk_min_order)
            if record.custom_sample_lead_time < 0:
                raise exceptions.ValidationError(
                    "Incorrect 'Sample Lead Time' value: %s" % record.custom_sample_lead_time)
            if record.custom_sample_max_order < 0:
                raise exceptions.ValidationError(
                    "Incorrect 'Sample Max Order' value: %s" % record.custom_sample_max_order)
            if record.custom_sample_min_order < 0:
                raise exceptions.ValidationError(
                    "Incorrect 'Sample Min Order' value: %s" % record.custom_sample_min_order)


class custom_test_result(models.Model):
    _name = 'custom_test_result'
    name = fields.Char()
