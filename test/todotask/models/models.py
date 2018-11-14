# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TodoTask(models.Model):
    _name = 'todo.task'

    name = fields.Char(string='描述', required=True)
    is_done = fields.Boolean('Done?')
    active = fields.Boolean('Active?', default=True,
                            domain=[('active','=',False)])

    @api.one
    def do_toggle_done(self):
        self.is_done = not self.is_done
        return True

    @api.multi
    def do_clear_done(self):
        done_recs = self.search([('is_done', '=', True)])
        done_recs.write({'active': False})
        return True


class TodoUser(models.Model):
    _inherit = 'todo.task'

    user_id = fields.Many2one('res.users', string='Responsible')
    date_deadline = fields.Date('Deadline')
    name = fields.Char(help='Can I help you?')
