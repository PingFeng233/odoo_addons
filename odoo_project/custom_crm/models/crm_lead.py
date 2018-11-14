# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Lead(models.Model):
    _name = "crm.lead"
    _inherit = "crm.lead"

    referred_by = fields.Char('Referred by')
    ballpark = fields.Text('Ballpark')
    sow = fields.Text('SOW')
