# -*- coding: utf-8 -*-
from odoo import http

class CustomProductVariant(http.Controller):
    @http.route('/index/', auth='public')
    def index(self, **kw):
        return "Hello, world"

#     @http.route('/custom_product_variant/custom_product_variant/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_product_variant.listing', {
#             'root': '/custom_product_variant/custom_product_variant',
#             'objects': http.request.env['custom_product_variant.custom_product_variant'].search([]),
#         })

#     @http.route('/custom_product_variant/custom_product_variant/objects/<model("custom_product_variant.custom_product_variant"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_product_variant.object', {
#             'object': obj
#         })