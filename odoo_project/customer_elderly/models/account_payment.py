# -*- coding: utf-8 -*-
import logging
import requests
import json
from odoo import models, fields, api


class ElderlyAccountPayment(models.Model):
    _inherit = 'account.payment'
    # is_petty_cash = fields.Boolean('零用錢')
    item_id = fields.Many2one('product.product', string='產品')
    upload_file = fields.Binary(string="上載附件")
    file_name = fields.Char(string="檔案名稱")
    quantity = fields.Float(string='數量')
    

    @api.onchange('item_id')
    def on_change_item_id(self):
        self.amount = self.item_id.list_price
        self.quantity = 1



