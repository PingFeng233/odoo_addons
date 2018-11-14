# -*- coding: utf-8 -*-
from odoo import http

# class CustomerElderly1(http.Controller):
#     @http.route('/customer_elderly1/customer_elderly1/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_elderly1/customer_elderly1/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_elderly1.listing', {
#             'root': '/customer_elderly1/customer_elderly1',
#             'objects': http.request.env['customer_elderly1.customer_elderly1'].search([]),
#         })

#     @http.route('/customer_elderly1/customer_elderly1/objects/<model("customer_elderly1.customer_elderly1"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_elderly1.object', {
#             'object': obj
#         })