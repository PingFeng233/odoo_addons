# -*- coding: utf-8 -*-
from odoo import http

# class HrDays(http.Controller):
#     @http.route('/hr_days/hr_days/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_days/hr_days/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_days.listing', {
#             'root': '/hr_days/hr_days',
#             'objects': http.request.env['hr_days.hr_days'].search([]),
#         })

#     @http.route('/hr_days/hr_days/objects/<model("hr_days.hr_days"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_days.object', {
#             'object': obj
#         })