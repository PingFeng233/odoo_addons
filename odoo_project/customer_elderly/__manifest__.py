# -*- coding: utf-8 -*-
{
    'name': "customer_elderly",

    'summary': """
    
    """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Wantech",
    'website': "http://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'wantech',
    'version': '0.9',

    # any module necessary for this one to work correctly
    'depends': ['base','web','account','account_reports','sale','sale_subscription','dev_print_cheque'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/report_paperformat.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/wantech_report_pdf.xml',
        'views/wantech_payment_receipt.xml',
        'views/account_payment_view.xml',
        'views/wantech_customers_receipt.xml',
        'views/wantech_payment_receipt_book.xml',
        'views/wantech_payment_receipt_deposit.xml',
        'views/wantech_pdf_layout.xml',
        'views/wantech_payment_to_invoice_receipt.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'qweb': [
        "static/src/xml/sale_subscription_dashboard_setup_bar.xml",
    ],
}