# -*- coding: utf-8 -*-
{
    'name': "休假管理",

    'summary': """
        休假考勤管理""",

    'description': """
        休假
    """,

    'author': "pf",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'TEST',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/add.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/data.xml',
    ],
}