# -*- coding: utf-8 -*-
from odoo import http

# class Todotask(http.Controller):
#     @http.route('/todotask/todotask/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/todotask/todotask/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('todotask.listing', {
#             'root': '/todotask/todotask',
#             'objects': http.request.env['todotask.todotask'].search([]),
#         })

#     @http.route('/todotask/todotask/objects/<model("todotask.todotask"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('todotask.object', {
#             'object': obj
#         })