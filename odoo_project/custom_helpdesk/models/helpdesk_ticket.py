# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = 'helpdesk.ticket'

    referred_by = fields.Char('Referred by')
    sloved_time = fields.Datetime('Sloved Time', readonly=True)
    ballpark = fields.Text('Ballpark')
    sow = fields.Text('SOW')

    @api.onchange('stage_id')
    def _create_sloved_time(self):
        self.ensure_one()
        if self.stage_id.name in [_('已解決'),_('已解决'), 'Solved']:
            self._origin.write({'sloved_time': fields.datetime.now()})
