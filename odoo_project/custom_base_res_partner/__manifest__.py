# -*- coding: utf-8 -*-
{
    'name': "custom_base_res_partner",

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
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','crm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/custom_base_res_partner_view.xml',
        'views/sequence_data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}