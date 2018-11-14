# -*- coding: utf-8 -*-
{
    'name': "todo task app",

    'summary': """
        任务管理""",

    'description': """
        工作计划管理系统：管理你的时间和工作安排
    """,

    'author': "pingfeng",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/todotask_security.xml',
        'views/views.xml',
        'views/add.xml',
        # 'views/task.xml',
        'views/todotask.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/data.xml',
    ],
    'application': True,
}
