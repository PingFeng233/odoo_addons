# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HolidaysType(models.Model):
    _name = "hr.holidays.status"
    _description = "Leave Type"
    name = fields.Char('Leave Type', required=True, translate=True)
    categ_id = fields.Many2one('calendar.event.type', string='Meeting Type')
    color_name = fields.Selection([
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('lightgreen', 'Light Green'),
        ('lightblue', 'Light Blue'),
        ('lightyellow', 'Light Yellow'),
        ('magenta', 'Magenta'),
        ('lightcyan', 'Light Cyan'),
        ('black', 'Black'),
        ('lightpink', 'Light Pink'),
        ('brown', 'Brown'),
        ('violet', 'Violet'),
        ('lightcoral', 'Light Coral'),
        ('lightsalmon', 'Light Salmon'),
        ('lavender', 'Lavender'),
        ('wheat', 'Wheat'),
        ('ivory', 'Ivory')], string='Color in Report', required=True, default='red')
    limit = fields.Boolean('Allow to Override Limit')
    active = fields.Boolean('Active', default=True)
    max_leaves = fields.Float(compute='_compute_leaves', string='Maximum Allowed')
    leaves_taken = fields.Float(compute='_compute_leaves', string='Leaves Already Taken')
    remaining_leaves = fields.Float(compute='_compute_leaves', string='Remaining Leaves')
    virtual_remaining_leaves = fields.Float(compute='_compute_leaves', string='Virtual Remaining Leaves')
    double_validation = fields.Boolean(string='Apply Double Validation')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    @api.multi
    def get_days(self, employee_id):
        # need to use `dict` constructor to create a dict per id
        result = dict(
            (id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in self.ids)

        holidays = self.env['hr.holidays'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.ids)
        ])


class Hr_days(models.Model):
    _name = "hr.holidays"
    _description = "休假"
    _inherit = ['mail.thread']

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char('Description')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm')
    payslip_status = fields.Boolean('Reported in last payslips')
    report_note = fields.Text('HR Comments')
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True,
                              default=lambda self: self.env.uid, readonly=True)
    date_from = fields.Datetime('Start Date', readonly=True, index=True, copy=False,
                                states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                track_visibility='onchange')
    date_to = fields.Datetime('End Date', readonly=True, copy=False,
                              states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                              track_visibility='onchange')
    holiday_status_id = fields.Many2one("hr.holidays.status", string="Leave Type", required=True, readonly=True,
                                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True,
                                  states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                  default=_default_employee, track_visibility='onchange')
    manager_id = fields.Many2one('hr.employee', string='Manager', readonly=True)
    notes = fields.Text('Reasons', readonly=True,
                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    number_of_days_temp = fields.Float(
        'Allocation', copy=False, readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help='Number of days of the leave request according to your working schedule.')
    number_of_days = fields.Float('Number of Days', compute='_compute_number_of_days', store=True,
                                  track_visibility='onchange')
    meeting_id = fields.Many2one('calendar.event', string='Meeting')
    type = fields.Selection([
        ('remove', 'Leave Request'),
        ('add', 'Allocation Request')
    ], string='Request Type', required=True, readonly=True, index=True, track_visibility='always', default='remove',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    parent_id = fields.Many2one('hr.holidays', string='Parent')
    linked_request_ids = fields.One2many('hr.holidays', 'parent_id', string='Linked Requests')
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    category_id = fields.Many2one('hr.employee.category', string='Employee Tag', readonly=True,
                                  states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                  help='Category of Employee')
    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('category', 'By Employee Tag')
    ], string='Allocation Mode', readonly=True, required=True, default='employee',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    first_approver_id = fields.Many2one('hr.employee', string='First Approval', readonly=True, copy=False,
                                        oldname='manager_id')
    second_approver_id = fields.Many2one('hr.employee', string='Second Approval', readonly=True, copy=False,
                                         oldname='manager_id2')
    double_validation = fields.Boolean('Apply Double Validation', related='holiday_status_id.double_validation')
    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')
