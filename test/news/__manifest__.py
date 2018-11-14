# -*- coding: utf-8 -*-
{
    'name': "News",

    'summary': """
        新闻""",

    'description': """
        新闻发布系统
    """,

    'author': "平风",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'web',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/base.xml',
        'views/add.xml',
        'views/index.xml',
        'views/detail.xml',
        'views/change.xml',
        'views/delete.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
