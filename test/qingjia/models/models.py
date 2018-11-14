# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Qingjd(models.Model):
    _name = 'qingjia.qingjiadan'

    WORKFLOW_STATE_SELECTION = {
        ('draft', '草稿'),
        ('confirm', '待审核'),
        ('reject', '拒绝'),
        ('complete', '已完成')
    }

    # 获取当前记录申请人姓名
    @api.model
    def _get_default_name(self):
        self._get_parent_id()
        for record in self:
            if not record.create_uid.name:
                record.name = self.env.user.name
            else:
                record.name = record.create_uid.name
        return self.env.user.name

    # 获取当前记录上级姓名
    @api.model
    def _get_default_manager(self):
        for record in self:
            # 已有记录
            uid = record.create_uid.id
            name = self.env['resource.resource'].search([('user_id', '=', uid)]).name
            employee = self.env['hr.employee'].search([('name', '=', name)])
            if not employee.parent_id.name:
                record.manager = employee.id
            else:
                record.manager = employee.parent_id

        # 新建记录
        uid = self.env.uid
        name = self.env['resource.resource'].search([('user_id', '=', uid)]).name
        employee = self.env['hr.employee'].search([('name', '=', name)])
        if not employee.parent_id.name:
            return employee.id
        else:
            return employee.parent_id

    # 获取上级的id
    @api.multi
    def _get_parent_id(self):
        for record in self:
            uid = record.create_uid.id
            name = self.env['resource.resource'].search([('user_id', '=', uid)]).name
            parent_name = self.env['hr.employee'].search([('name', '=', name)]).parent_id.name
            if not parent_name:
                parent_name = 'Administrator'
            parent_id = self.env['resource.resource'].search([('name', '=', parent_name)]).user_id
            self.env.cr.execute(
                "update qingjia_qingjiadan set parent_id='%d' where id='%d';" % (parent_id, record.id)
            )

    _defaults = {
        'name': _get_default_name,
        'manager': _get_default_manager,
        'parent_id': _get_parent_id,
    }

    name = fields.Char(string='申请人', required=True, readonly=True, help='申请人',
                       compute='_get_default_name', default=_defaults['name'])
    manager = fields.Many2one('hr.employee', string='主管', required=True,
                              readonly=True, compute='_get_default_manager', default=_defaults['manager'])
    days = fields.Integer(string="天数")
    startdate = fields.Date(string="开始日期")
    reason = fields.Text(string="请假事由")
    state = fields.Selection(WORKFLOW_STATE_SELECTION,
                             default='draft',
                             string='状态',
                             readonly=True)
    is_owner = fields.Boolean(help='记录所有者是否是自己', compute='_get_is_owner')
    is_manager = fields.Boolean(help='当前用户是否是该记录的上级', compute='_get_is_manager')

    parent_id = fields.Integer(readonly=True, default=_defaults['parent_id'])

    # 判断当前记录是否是当前记录的
    @api.multi
    def _get_is_owner(self):
        for record in self:
            if record.create_uid.id == self.env.uid:
                record.is_owner = True
            else:
                record.is_owner = False

    # 判断当前记录的上级是否是当前用户
    @api.multi
    def _get_is_manager(self):
        for record in self:
            if record.parent_id == self.env.uid:
                record.is_manager = True
            else:
                record.is_manager = False

    # 自定义工作流状态转换的方法
    @api.multi
    def do_confirm(self):
        return self.write({'state': 'confirm'})

    @api.multi
    def do_reject(self):
        return self.write({'state': 'reject'})

    @api.multi
    def do_complete(self):
        return self.write({'state': 'complete'})
