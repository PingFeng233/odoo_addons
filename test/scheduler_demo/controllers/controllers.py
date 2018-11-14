# -*- coding: utf-8 -*-
from odoo import http

# class SchedulerDemo(http.Controller):
#     @http.route('/scheduler_demo/scheduler_demo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/scheduler_demo/scheduler_demo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('scheduler_demo.listing', {
#             'root': '/scheduler_demo/scheduler_demo',
#             'objects': http.request.env['scheduler_demo.scheduler_demo'].search([]),
#         })

#     @http.route('/scheduler_demo/scheduler_demo/objects/<model("scheduler_demo.scheduler_demo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('scheduler_demo.object', {
#             'object': obj
#         })