# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_abstract_payment(models.AbstractModel):
    _name = "account.abstract.payment"
    _inherit = "account.abstract.payment"

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
            companies = self.env['res.company'].search(
                [('parent_id', '=', self.env.user.company_id.id)]) + self.env.user.company_id
            return {'domain': {
                'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)],
                'journal_id': [('type', 'in', ('bank', 'cash', 'general')),
                               ('company_id', 'child_of', companies.ids)]}}
        return {}
