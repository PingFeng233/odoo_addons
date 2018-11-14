# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class Reaccount_payment(models.Model):
    _inherit = 'account.payment'
    move_name = fields.Char(string='Journal Entry Name', readonly=False,
        default=False, copy=False,
        help="Technical field holding the number given to the journal entry, automatically set when the statement line is reconciled then stored to set the same number again if the line is cancelled, set to draft and re-processed again.")

