# -*- coding: utf-8 -*-
import json
import io
import datetime

from odoo import models, fields, api
from odoo.tools.translate import _

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter


# from odoo.enterprise.account_reports.models.account_financial_report import

class Bnt(models.Model):
    _inherit = 'account.invoice'
    _name = 'bnt.bnt'


class bnt_report(models.AbstractModel, ):
    _inherit = 'account.report'
    _name = 'report.bnt.custom_report'

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}

    @api.model
    def get_lines(self, options, line_id=None):
        dt_to = options['date'].get('date_to') or options['date'].get('date')
        dt_from = options['date'].get('date_from', False)
        invoices = self.env['account.invoice'].search([('date', '>=', dt_from), ('date', '<=', dt_to)])
        invoice_lines = self.env['account.invoice.line'].search([])
        products = self.env['product.template'].search([])
        # rows = [{'unfoldable': False, 'level': 2, 'id': '2', 'columns': [{} for i in xrange(len(products) + 4)],
        #          'name': ''}]
        rows = []
        for i in xrange(len(invoices)):
            line_name = []
            product_values = [{"name": ''} for n in xrange(len(products))]
            for line in invoice_lines.search([('invoice_id', '=', invoices[i].id)]):
                line_name.append(line.name)
                for j in xrange(len(products)):
                    if products[j].id == line.product_id.id:
                        product_values[j] = {"name": line.price_total}
                    if products[j].name == u'其他':
                        other = product_values[j]
                        index = j
            del product_values[index]
            product_values.append(other)

            invoice_name = '-'.join(line_name)

            values = [{"name": i + 1},
                      {"name": invoices[i].date},
                      {"name": invoice_name}]
            for k in product_values:
                values.append(k)

            values.append({"name": invoices[i].amount_total})
            rows.append({'name': '', 'level': 3,
                         'unfoldable': False, 'id': 1,
                         'columns': values,
                         })
        return rows

    def get_columns_name(self, options):
        values = [{}, {"name": u'序号'}, {"name": u'日期'}, {"name": u'费用内容'}]
        for i in [{"name": product.name}
                  for product in self.env['product.template'].search([])]:
            values.append(i)
        del values[values.index({"name": u'其他'})]
        values.append({"name": u'其他'})
        values.append({"name": u'合计'})
        return values

    def get_report_name(self):
        return (u'测试报表')

    def get_xlsx(self, options, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self.get_report_name()[:31])

        def_style = workbook.add_format({'font_name': 'Arial'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True})
        level_0_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'bottom': 2})
        # sheet.set_column(0, 0, 15)  # Set the first column width to 15

        sheet.write(0, 0, u'零用金月报', title_style)
        sheet.write(2, 0, u'院舍名称：%s' % (self.env.user.company_id.name), title_style)
        sheet.write(3, 0, u'地址：%s' % (self.env.user.company_id.partner_id.street +
                                      self.env.user.company_id.partner_id.street2), title_style)
        now = datetime.datetime.now()
        sheet.write(4, 0, u'时段：%s' % (str(now.year) + '-' + str(now.month)), title_style)

        y_offset = 6
        x = 0
        for column in self.get_columns_name(options)[1:]:
            sheet.write(y_offset, x, column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' '), level_0_style)
            x += 1

        ctx = self.set_context(options)
        ctx.update({'no_format': True, 'print_mode': True})
        lines = self.with_context(ctx).get_lines(options)

        y_offset = 7
        for i in xrange(len(lines)):
            datas = lines[i]['columns']
            for j in xrange(len(datas)):
                sheet.write(y_offset, j, datas[j]['name'], def_style)
            y_offset += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


@api.multi
def get_report_values(self, docids, data=None):
    invoices = self.env['account.invoice'].search([])
    invoice_lines = self.env['account.invoice.line'].search([])
    products = self.env['product.template'].search([])
    values = [{"is_bold": False, "value": u'日期'}, {"is_bold": False, "value": u'费用内容'}]
    for i in [{"is_bold": False, "value": product.name}
              for product in self.env['product.template'].search([])]:
        values.append(i)
    values.append({"is_bold": False, "value": u'合计'})

    rows = [{
        "id": 0,
        "_ids": [1],
        "indent": 1,
        "title": "序号",
        "expanded": True,
        "values": values
    }]

    for i in xrange(len(invoices)):
        line_name = []
        product_values = [{"is_bold": False, "value": ''} for n in xrange(len(products))]
        for line in invoice_lines.search([('invoice_id', '=', invoices[i].id)]):
            line_name.append(line.name)
            for j in xrange(len(products)):
                if products[j].id == line.product_id.id:
                    product_values[j] = {"is_bold": False, "value": line.price_total}

        invoice_name = '-'.join(line_name)

        values = [{"is_bold": False, "value": invoices[i].date},
                  {"is_bold": False, "value": invoice_name}]
        for k in product_values:
            values.append(k)
        values.append({"is_bold": False, "value": invoices[i].amount_total})

        rows.append({
            "id": invoices[i].id,
            "_ids": [1],
            "indent": 1,
            "title": i + 1,
            "expanded": True,
            "values": values
        })
    data = {
        "headers": [[{"width": 3 + int(len(products)), "height": 2, "title": "测试报表",
                      "id": 1, "expanded": False}]],
        "measure_row": [{"measure": "BB", "is_bold": False, "id": 1}, {"measure": "AA", "is_bold": False, "id": 1}],
        "rows": rows,
        "nbr_measures": 3 + int(len(products)),
        "title": "发票报表"
    }
    lines = json.dumps(data)
    return {'data': data, 'lines': lines}
