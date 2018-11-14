# -*- coding: utf-8 -*-
from odoo import http

# class CustomHelpdesk(http.Controller):
#     @http.route('/custom_helpdesk/custom_helpdesk/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_helpdesk/custom_helpdesk/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_helpdesk.listing', {
#             'root': '/custom_helpdesk/custom_helpdesk',
#             'objects': http.request.env['custom_helpdesk.custom_helpdesk'].search([]),
#         })

#     @http.route('/custom_helpdesk/custom_helpdesk/objects/<model("custom_helpdesk.custom_helpdesk"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_helpdesk.object', {
#             'object': obj
#         })