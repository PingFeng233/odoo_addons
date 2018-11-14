# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Custom_project(models.Model):
    _inherit = 'project.project'
    _name = 'project.project'

    project_status = fields.Many2one('custom_project_status', string='Project Status')
    schedule_complete_date = fields.Date('Schedule Complete Date')
    planned_hours = fields.Float('Planned Hours', digits=(4, 2))
    real_time = fields.Float('Real Time', digits=(4, 2), compute='_compute_real_time')

    @api.constrains('planned_hours')
    def _check_planned_hours(self):
        self.ensure_one()
        if self.planned_hours < 0:
            raise ValidationError('Planned Hours 不能小于0!')

    @api.multi
    def _compute_real_time(self):
        for record in self:
            try:
                real_time = sum(
                    [i.unit_amount for i in self.env['account.analytic.line'].
                        search([('project_id', '=', record.id)])])
            except:
                real_time = 0.0
            record.real_time = real_time
        self._change_action_view_model()

    @api.model
    def _change_action_view_model(self):
        act_id = self.env['ir.model.data'].sudo().search([('name', '=', 'open_view_project_all')])[0].res_id
        record = self.env['ir.actions.act_window'].sudo().search([('id', '=', act_id)])[0]
        if record.view_mode == 'tree,form':
            record.write({'view_mode': 'tree,form,kanban,calendar'})


class custom_project_status(models.Model):
    _name = 'custom_project_status'
    _order = "sequence, name, id"

    name = fields.Char('项目状态')
    sequence = fields.Integer()


class Task(models.Model):
    _name = "project.task"
    _inherit = "project.task"

    new_priority = fields.Selection([
        ('0', '低'),
        ('1', '中'),
        ('2', '高')
    ], default='0', index=True, string="Priority")
