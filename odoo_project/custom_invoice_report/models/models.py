# -*- coding: utf-8 -*-
import datetime
import io

from odoo import models, fields, api

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter


# from odoo.enterprise.account_reports.models.account_financial_report import


class Custom_invoice_report(models.AbstractModel, ):
    _inherit = 'account.report'
    _name = 'report.custom_invoice_report.custom_report'

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}

    def get_lines(self, options, line_id=None):
        dt_to = options['date'].get('date_to') or options['date'].get('date')
        dt_from = options['date'].get('date_from', False)

        invoices = self.env['account.invoice'].search([('date', '>=', dt_from), ('date', '<=', dt_to),
                                                       ('state', '=', 'paid'), ('money_extra', '=', True)])
        invoice_lines = self.env['account.invoice.line'].search([])
        selected_company_ids = self.get_selected_company_ids(options)
        if selected_company_ids:
            invoices = self.env['account.invoice'].search([('date', '>=', dt_from), ('date', '<=', dt_to),
                                                           ('company_id.id', 'in', selected_company_ids),
                                                           ('state', '=', 'paid'), ('money_extra', '=', True)])
            invoice_lines = self.env['account.invoice.line'].search(
                [('company_id.id', 'in', selected_company_ids)])

        categories = self.env['product.category'].search([])
        rows = []
        for i in xrange(len(invoices)):
            line_name = []
            product_values = [{"name": ''} for n in xrange(len(categories))]
            for line in invoice_lines.filtered(lambda r: r.invoice_id.id == invoices[i].id):
                line_name.append(line.name)
                for j in xrange(len(categories)):
                    if categories[j].id == line.product_id.product_tmpl_id.categ_id.id:
                        product_values[j] = {"name": line.price_total}
                    if categories[j].name == u'其他':
                        other = product_values[j]
                        index = j
            try:
                del product_values[index]
                product_values.append(other)
            except:
                pass

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
        values = [{}, {"name": u'序號'}, {"name": u'日期'}, {"name": u'費用內容'}]
        for i in [{"name": category.name}
                  for category in self.env['product.category'].search([])]:
            values.append(i)
        try:
            del values[values.index({"name": u'其他'})]
            values.append({"name": u'其他'})
        except:
            pass
        values.append({"name": u'合共'})
        return values

    def get_report_name(self):
        return (u'零用現金報表')

    def get_title_name(self):
        return u'零用現金報表'

    def get_selected_company_ids(self, options):
        multi_company = options.get('multi_company', None)
        selected_company_ids = []
        if multi_company:
            for c in multi_company:
                if c['selected']:
                    selected_company_ids.append(c['id'])
        return selected_company_ids

    def get_company_name(self, options):
        try:
            company_name = self.env.user.company_id.name
        except:
            company_name = ''
        multi_company = options.get('multi_company', None)
        selected_company_ids = self.get_selected_company_ids(options)
        if multi_company:
            if selected_company_ids:
                name = [c.name for c in self.env['res.company'].search([('id', 'in', selected_company_ids)])]
            else:
                companies = options['multi_company']
                name = [c.get('name', '') for c in companies]
            company_name = ' | '.join(name)
        return company_name

    def get_company_address(self, options):
        try:
            address = self.env.user.company_id.partner_id.street + \
                      self.env.user.company_id.partner_id.street2
        except:
            address = ''

        multi_company = options.get('multi_company', None)
        selected_company_ids = self.get_selected_company_ids(options)
        if multi_company:
            if selected_company_ids:
                companiy_ids = selected_company_ids
            else:
                companies = options['multi_company']
                companiy_ids = [c.get('id', None) for c in companies]

            address = []
            for c in self.env['res.company'].search([('id', 'in', companiy_ids)]):
                try:
                    address.append((c.partner_id.street or '') + (c.partner_id.street2 or ''))
                except:
                    address.append('')
            address = ' | '.join(address)
        return address

    def get_xlsx(self, options, response):
        title_name = self.get_title_name()
        name = self.get_company_name(options)
        address = self.get_company_address(options)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self.get_report_name()[:31])

        def_style = workbook.add_format({'font_name': 'Arial'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True})
        level_0_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'bottom': 2})
        # sheet.set_column(0, 0, 15)  # Set the first column width to 15

        now = datetime.datetime.now()

        sheet.write(0, 0, title_name, title_style)
        sheet.write(2, 0, u'院舍名稱：%s' % (name), title_style)
        sheet.write(3, 0, u'地址：%s' % (address), title_style)
        sheet.write(4, 0, u'時段：%s' % (str(now.year) + '-' + str(now.month)), title_style)

        y_offset = 6
        x = 0
        for column in self.get_columns_name(options)[1:]:
            sheet.write(y_offset, x, column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' '), level_0_style)
            x += 1

        ctx = self.set_context(options)
        ctx.update({'no_format': True, 'print_mode': True})
        lines = self.with_context(ctx).get_lines(options)

        y_offset = 7
        if lines:
            for i in xrange(len(lines)):
                datas = lines[i]['columns']
                for j in xrange(len(datas)):
                    sheet.write(y_offset, j, datas[j]['name'], def_style)
                y_offset += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


class Custom_invoice_rec_report(models.AbstractModel):
    _inherit = 'report.custom_invoice_report.custom_report'
    _name = 'report.custom_invoice_rec_report.custom_report'

    def get_report_name(self):
        return (u'每月收賬報表')

    def get_title_name(self):
        return u'每月收賬報表'

    def get_columns_name(self, options):
        values = [{}, {"name": u'收據編號'}, {"name": u'收據日期'},
                  {"name": u'院友姓名'}, {"name": u'收據金額'}, {"name": u'按金'}, {"name": u'訂金'}]
        for i in [{"name": product.name}
                  for product in self.env['product.category'].search([])]:
            values.append(i)
        try:
            del values[values.index({"name": u'其他'})]
            values.append({"name": u'其他'})
        except:
            pass
        values += [{'name': u'增值税'}, {"name": u'現金'}, {"name": u'支票'}, {"name": u'總數'}]
        return values

    def get_lines(self, options, line_id=None):
        dt_to = options['date'].get('date_to') or options['date'].get('date')
        dt_from = options['date'].get('date_from', False)

        payments = self.env['account.payment'].search(
            [('payment_date', '>=', dt_from), ('payment_date', '<=', dt_to),
             ('state', '!=', 'draft')])
        selected_company_ids = self.get_selected_company_ids(options)

        if selected_company_ids:
            payments = self.env['account.payment'].search(
                [('payment_date', '>=', dt_from), ('payment_date', '<=', dt_to),
                 ('company_id.id', 'in', selected_company_ids),
                 ('state', '!=', 'draft')])
        rows = []
        for i in xrange(len(payments)):
            number = payments[i].name
            payment_date = payments[i].payment_date
            name = payments[i].partner_id.name
            amount = payments[i].amount
            deposit = ''
            order = ''
            cash = ''
            check = ''
            tax = ''
            try:
                invoice_id = self.env['account.invoice'].search([
                    ('payment_ids', '=', payments[i].id)])[0].id
            except:
                invoice_id = None
            categories = self.env['product.category'].search([])
            product_values = [{'name': ''} for j in xrange(len(categories))]
            if payments[i].journal_id.name == u'按金現金':
                deposit = payments[i].amount
                cash = payments[i].amount
                total = deposit
            elif payments[i].journal_id.name == u'按金支票':
                deposit = payments[i].amount
                check = payments[i].amount
                total = deposit
            elif payments[i].journal_id.name == u'訂金現金':
                order = payments[i].amount
                cash = payments[i].amount
                total = order
            elif payments[i].journal_id.name == u'訂金支票':
                order = payments[i].amount
                check = payments[i].amount
                total = order
            elif payments[i].journal_id.name == u'現金':
                cash = payments[i].amount
                total = cash
            elif payments[i].journal_id.name == u'支票':
                check = payments[i].amount
                total = check
            else:
                invoice_lines = self.env['account.invoice.line'].search([])
                tax_line = self.env['account.move.line'].search([
                    ('invoice_id', '=', invoice_id), ('tax_line_id', '!=', None)])
                if tax_line:
                    tax = tax_line[0].credit

                if invoice_id:
                    total = self.env['account.invoice'].search([('id', '=', invoice_id)])[0].amount_total
                    for line in invoice_lines.search([('invoice_id', '=', invoice_id)]):
                        for j in xrange(len(categories)):
                            if categories[j].id == line.product_id.product_tmpl_id.categ_id.id:
                                product_values[j] = {"name": line.price_subtotal}
                            if categories[j].name == u'其他':
                                other = product_values[j]
                                index = j
                    try:
                        del product_values[index]
                        product_values.append(other)
                    except:
                        pass
                else:
                    total = amount
            values = [{'name': number},
                      {'name': payment_date},
                      {'name': name},
                      {'name': amount},
                      {'name': deposit},
                      {'name': order}]
            for k in product_values:
                values.append(k)
            values += [{'name': tax}, {'name': cash}, {'name': check}, {'name': total}]
            rows.append({'name': '', 'level': 3,
                         'unfoldable': False, 'id': 1,
                         'columns': values,
                         })
        return rows

#
# class AccountInvoice(models.Model):
#     _inherit = "account.invoice"
#
#     money_extra = fields.Boolean(string="零用現金", default=False)


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = "product.category"
    _order = 'sequence,id'

    sequence = fields.Integer(help='Used to order Journals in the dashboard view', default=99)

    @api.multi
    def change_default_sequence(self):
        for r in self:
            if r.sequence == None:
                r.sequence = 99
