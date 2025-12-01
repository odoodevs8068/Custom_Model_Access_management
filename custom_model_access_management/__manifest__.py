{
    'name': 'Access Management - Model/User Wise',
    'version': '1.2',
    'category': 'Extra Tools',
    'author': "JD DEVS",
    'depends': ['base', 'base_setup', 'mail', 'web', 'account', 'sale'],
    'data': [
        'security/model_access_rights_groups.xml',
        'security/ir.model.access.csv',
        'views/ir_model_inherit.xml',
        'views/access_rights_views.xml',
        'views/export.xml',
        'views/settings.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Actions
            "custom_model_access_management/static/src/js/action_menu/action_menu.js",

            # chatter
            "custom_model_access_management/static/src/js/chatter/chatter_patch.js",

            # List
            "custom_model_access_management/static/src/js/list/list_arch_praser.js",
            "custom_model_access_management/static/src/js/list/list_patch.js",
            "custom_model_access_management/static/src/js/list/list_render.js",

            #FORM
            "custom_model_access_management/static/src/js/form/form_patch.js",
            "custom_model_access_management/static/src/js/form/form_arch_praser.js",
            "custom_model_access_management/static/src/js/form/form_compiler.js",

            # Kanban
            "custom_model_access_management/static/src/js/kanban/kanban_patch.js",

            # Export_xlsx
            "custom_model_access_management/static/src/js/export_xlsx/export.js",

            # fields
            "custom_model_access_management/static/src/js/fields/relational_utils.js",
            "custom_model_access_management/static/src/js/fields/x2many.js",

            # dialog
            "custom_model_access_management/static/src/js/dialog/select_create_dialog.js",

            # Notebook
            "custom_model_access_management/static/src/js/notebook/notebook_page.js",
            "custom_model_access_management/static/src/js/list/add_button_dialog.js",

            # Search
            "custom_model_access_management/static/src/js/search/search_patch.js",
            "custom_model_access_management/static/src/views/serach_bar_menu.xml",

            # XML
            "custom_model_access_management/static/src/views/ListViewdocumentupload.xml",
            "custom_model_access_management/static/src/views/chatter.xml",
            "custom_model_access_management/static/src/views/add_button_dialog.xml",

            "custom_model_access_management/static/src/js/model_access_utils.js",
        ]
    },
    'price': 533.22,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'images': ['static/description/assets/screenshots/banner.png'],
}

