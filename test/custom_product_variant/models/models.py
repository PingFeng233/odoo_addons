# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import http
from ..controllers.controllers import CustomProductVariant


class Custom_product_variant(models.Model):
    _name = "product.template"
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        product = super(Custom_product_variant, self.with_context(create_product_product=True)).create(vals)
        self.variant_action()
        return product,{
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'list,form',
            'view_type': 'tree',
            'name': u'查看出/入库单',
            'views': 'product.template.product.tree',
        }

    @api.multi
    def variant_action(self):
        print('--------------')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'list,form',
            'view_type': 'tree',
            'name': u'查看出/入库单',
            'views': 'product.template.product.tree',
        }
