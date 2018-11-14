from odoo import models, fields, api


class Sale_report_2D(models.AbstractModel):
    _name = 'sale.report.2d'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('sale.report.2d')
        spk = self.env['sale.order.line'].search([('id', '=', docids)])
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self,
            'abc': '3.1415926'
        }
        return report_obj.render('stock_report.stock_picking_report', docargs)