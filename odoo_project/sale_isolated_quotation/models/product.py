# coding:utf8

from odoo import api, models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_variants = fields.Boolean('Has Variants', default=False)


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        attribute_value_ids = []
        for i in self.env['product.product'].search([('product_tmpl_id.id', '=', vals.get('product_tmpl_id',None))]):
            attribute_value_ids.append([k.id for k in i.attribute_value_ids])
        if (attribute_value_ids != [] and attribute_value_ids.count([]) < 1) or(
                attribute_value_ids and attribute_value_ids.count([]) < 2):
            super(ProductProduct, self.with_context(create_product_product=True)).create(
                {'product_tmpl_id': vals['product_tmpl_id'],
                 'attribute_value_ids': [(6, 0, [])]})
            attribute_value_ids.append([])

        product = super(ProductProduct, self.with_context(create_product_product=True)).create(vals)

        if attribute_value_ids.count([]) == 2:
            product_tmps = self.env['product.product'].search([
                ('product_tmpl_id.id', '=', vals['product_tmpl_id'])]) - self.env['product.product'].search([
                ('product_tmpl_id.id', '=', vals['product_tmpl_id']), ('attribute_value_ids.id', '!=', [])])
            product_tmps[0].unlink()

        # When a unique variant is created from tmpl then the standard price is set by _set_standard_price
        if not (self.env.context.get('create_from_tmpl') and len(product.product_tmpl_id.product_variant_ids) == 1):
            product._set_standard_price(vals.get('standard_price') or 0.0)
        return product

