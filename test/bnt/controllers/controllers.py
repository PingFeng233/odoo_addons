# -*- coding: utf-8 -*-
import json
import StringIO
import datetime

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.pivot import TableExporter
from odoo.tools.misc import xlwt
from odoo.tools import ustr
from odoo.exceptions import Warning
from collections import deque


class Bnt(TableExporter):
    @http.route('/bnt/print_excel/', auth="user")
    def export_xls(self, **kw):

        jdata = json.loads(kw['data'])
        token = kw['token']
        month = kw.get('month', None)
        month = datetime.datetime.strptime(str(month), '%Y-%m') if month else None
        rows = jdata['rows']
        new_rows = [rows[0]]

        if month:
            for row in rows[1:]:
                cur_month = str(row['values'][0]['value']).rsplit('-', 1)[:-1][0]
                cur_month = datetime.datetime.strptime(cur_month, '%Y-%m')
                if cur_month == month:
                    new_rows.append(row)
            jdata['rows'] = new_rows

        nbr_measures = jdata['nbr_measures']
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(jdata['title'])
        header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
        header_plain = xlwt.easyxf("pattern: pattern solid, fore_colour gray25;")
        bold = xlwt.easyxf("font: bold on;")

        # Step 1: writing headers
        headers = jdata['headers']

        # x,y: current coordinates
        # carry: queue containing cell information when a cell has a >= 2 height
        #      and the drawing code needs to add empty cells below
        x, y, carry = 1, 0, deque()
        for i, header_row in enumerate(headers):
            # worksheet.write(i, 0, '', header_plain)
            for header in header_row:
                while (carry and carry[0]['x'] == x):
                    cell = carry.popleft()
                    for i in range(nbr_measures):
                        worksheet.write(y, x + i, '', header_plain)
                    if cell['height'] > 1:
                        carry.append({'x': x, 'height': cell['height'] - 1})
                    x = x + nbr_measures
                style = header_plain if 'expanded' in header else header_bold
                for i in range(header['width']):
                    worksheet.write(y, x + i, header['title'] if i == 0 else '', style)
                    # worksheet.write(y, 0, header['title'] if i == 0 else '', style)
                if header['height'] > 1:
                    carry.append({'x': x, 'height': header['height'] - 1})
                x = x + header['width']
            while (carry and carry[0]['x'] == x):
                cell = carry.popleft()
                for i in range(nbr_measures):
                    worksheet.write(y, x + i, '', header_plain)
                if cell['height'] > 1:
                    carry.append({'x': x, 'height': cell['height'] - 1})
                x = x + nbr_measures
            x, y = 1, y + 1

        # Step 2: measure row
        if nbr_measures > 1:
            # worksheet.write(y, 0, '', header_plain)
            for measure in jdata['measure_row']:
                style = header_bold if measure['is_bold'] else header_plain
                worksheet.write(y, 0, measure['measure'], style)
                # x = x + 1
                y = y + 1

        # Step 3: writing data
        x = 0
        for row in jdata['rows']:
            worksheet.write(y, x, row['indent'] * '     ' + ustr(row['title']), header_plain)
            for cell in row['values']:
                x = x + 1
                if cell.get('is_bold', False):
                    worksheet.write(y, x, cell['value'], bold)
                else:
                    worksheet.write(y, x, cell['value'])
            x, y = 0, y + 1

        response = request.make_response(None,
                                         headers=[('Content-Type', 'application/vnd.ms-excel'),
                                                  ('Content-Disposition', 'attachment; filename=table.xls;')],
                                         cookies={'fileToken': token})
        workbook.save(response.stream)
        return response
