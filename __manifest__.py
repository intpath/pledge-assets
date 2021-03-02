# -*- coding: utf-8 -*-
{
    'name': "Pledges",

    'summary': """
        For Creating & Managing Pledges""",

    'author': "Inteferated Path",
    'website': "https://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1',
    'application':True,

    # any module necessary for this one to work correctly
    'depends': ['base','mail','contacts'],

    # always loaded
    'data': [
        'security/res_groups_data.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/pledge_pledge_views.xml',
        'views/pledge_bank_views.xml',
        'views/res_partner_view.xml',
        'views/res_config_view.xml'
    ],
}
