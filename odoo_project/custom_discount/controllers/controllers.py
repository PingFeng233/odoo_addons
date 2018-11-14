# -*- coding: utf-8 -*-
from odoo import http

# class CustomDiscount(http.Controller):
#     @http.route('/custom_discount/custom_discount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_discount/custom_discount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_discount.listing', {
#             'root': '/custom_discount/custom_discount',
#             'objects': http.request.env['custom_discount.custom_discount'].search([]),
#         })

#     @http.route('/custom_discount/custom_discount/objects/<model("custom_discount.custom_discount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_discount.object', {
#             'object': obj
#         })