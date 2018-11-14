# coding:utf-8
from odoo import api, models, fields
from odoo.exceptions import ValidationError


class Custom_product_template(models.Model):
    _inherit = 'product.template'

    #   general_information
    is_material = fields.Boolean(string="Is Material", default=False)
    is_product = fields.Boolean(string="Is Product", default=False)
    short_description = fields.Char(string='Short Description',translate=True)
    description = fields.Text(string='Description',translate=True)
    paper_no = fields.Text(string='Paper No.')
    season = fields.Many2one('custom_season', string='Season')
    brand = fields.Many2one('custom_brand', string='Brand')
    in_charge = fields.Many2one('hr.employee', string='Brand')
    status = fields.Many2one('custom_status', string='Status')
    material_type = fields.Many2one('custom_material_type', string='Material Type')
    user_status = fields.Many2one('custom_user_status', string='User Status')
    method = fields.Many2one('custom_method', string='Method')
    ingredient = fields.Many2one('custom_ingredient', string='Ingredient(成份)')
    yarn_count = fields.Many2one('custom_yarn_count', string='組織/紗支數')
    weight = fields.Float(string='Weight', digits=(12, 2))
    region = fields.Many2one('custom_region', string='Region(地區)')
    remark = fields.Text('Remark')
    process1 = fields.Char('後處理1')
    process2 = fields.Char('後處理2')

    @api.constrains('weight')
    def _check_float_field(self):
        for record in self:
            if record.weight < 0:
                raise ValidationError('weight不能小于0')


class Custom_season(models.Model):
    _name = 'custom_season'
    name = fields.Char()


class Custom_brand(models.Model):
    _name = 'custom_brand'
    name = fields.Char()


class Custom_status(models.Model):
    _name = 'custom_status'
    name = fields.Char()


class Custom_user_status(models.Model):
    _name = 'custom_user_status'
    name = fields.Char()


class Custom_material_type(models.Model):
    _name = 'custom_material_type'
    name = fields.Char()


class Custom_method(models.Model):
    _name = 'custom_method'
    name = fields.Char()


class Custom_ingredient(models.Model):
    _name = 'custom_ingredient'
    name = fields.Char()

class Custom_yarn_count(models.Model):
    _name = 'custom_yarn_count'
    name = fields.Char()