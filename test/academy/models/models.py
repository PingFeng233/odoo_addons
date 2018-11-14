# -*- coding: utf-8 -*-

from odoo import models, fields, api


class academy(models.Model):
    _name = 'academy.teachers'

    name = fields.Char('教师')
    biography = fields.Html('简介')
    course_ids = fields.One2many('product.template', 'teacher_id', string='课程')


class Courses(models.Model):
    # _name = 'academy.courses'
    _inherit = 'product.template'

    # name = fields.Char(string='课程')
    teacher_id = fields.Many2one('academy.teachers', string='Teacher')
