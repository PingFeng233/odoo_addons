# -*- coding: utf-8 -*-
from odoo import http

# class CustomProductTemplate(http.Controller):
#     @http.route('/custom_product_template/custom_product_template/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_product_template/custom_product_template/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_product_template.listing', {
#             'root': '/custom_product_template/custom_product_template',
#             'objects': http.request.env['custom_product_template.custom_product_template'].search([]),
#         })

#     @http.route('/custom_product_template/custom_product_template/objects/<model("custom_product_template.custom_product_template"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_product_template.object', {
#             'object': obj
#         })