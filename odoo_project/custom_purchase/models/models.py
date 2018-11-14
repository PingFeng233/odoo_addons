# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"

    pur_type = fields.Selection([
        ('purchase', 'Vendor Bill'),
        ('debit_note', 'Debit Note')
    ], string='Type', default='purchase', required=True)


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = "account.move"

    @api.multi
    def post(self):
        invoice = self._context.get('invoice', False)
        self._post_validate()
        for move in self:
            move.line_ids.create_analytic_lines()
            if move.name == '/':
                new_name = False
                journal = move.journal_id
                if invoice and invoice.pur_type == 'debit_note':
                    try:
                        move_name = self.env['ir.sequence'].next_by_code('custom.purchase.order')
                        invoice.write({'move_name': move_name})
                    except:
                        raise UserError(_('Please define a sequence'))

                if invoice and invoice.move_name and invoice.move_name != '/':
                    new_name = invoice.move_name
                else:
                    if journal.sequence_id:
                        # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
                        sequence = journal.sequence_id
                        if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
                            if not journal.refund_sequence_id:
                                raise UserError(_('Please define a sequence for the credit notes'))
                            sequence = journal.refund_sequence_id

                        new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                    else:
                        raise UserError(_('Please define a sequence on the journal.'))

                if new_name:
                    move.name = new_name
        return self.write({'state': 'posted'})
