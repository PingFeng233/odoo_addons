# -*- coding: utf-8 -*-
{
    'name': "custom_invoice_report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "WANTECH Innovation Technology Ltd.",
    'website': "http://www.wantech.com.hk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'test',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_reports'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/custom_invoice_report.xml',
        'views/data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/data.xml',
    ],
}
