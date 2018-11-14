# -*- coding: utf-8 -*-
from odoo import http

# class CustomPayment(http.Controller):
#     @http.route('/custom_payment/custom_payment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_payment/custom_payment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_payment.listing', {
#             'root': '/custom_payment/custom_payment',
#             'objects': http.request.env['custom_payment.custom_payment'].search([]),
#         })

#     @http.route('/custom_payment/custom_payment/objects/<model("custom_payment.custom_payment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_payment.object', {
#             'object': obj
#         })