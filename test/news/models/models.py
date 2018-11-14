# -*- coding: utf-8 -*-
from odoo import models, fields, api


class News(models.Model):
    _name = 'news.news'

    title = fields.Char('标题')
    content = fields.Text('内容')
    author = fields.Char('作者')
    pub_time = fields.Datetime('发布时间', default=fields.Datetime.now)
    category = fields.Many2one('news.category', string='类别')
    is_delete = fields.Boolean('删除', default=False)

    @api.model
    def order_by(self, key):
        if key.startswith('-'):
            key = key[1:]
            return self.sorted(key=key, reverse=True)
        else:
            return self.sorted(key=key)

    @api.model
    def create(self, vals):
        uid = self.env.uid
        author = self.env['resource.resource'].search([('user_id', '=', uid)]).name
        vals['author'] = author
        return super(News, self).create(vals)


class Category(models.Model):
    _name = 'news.category'

    name = fields.Char('名称')

    # 序列化,把python对象转换成dict,方便json使用
    @api.model
    def cate2dict(self):
        return {'name': self.name}
