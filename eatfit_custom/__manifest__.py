# -*- coding: utf-8 -*-
{
    'name': "eatfit_custom V13",
    'author': "NBC IT",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','sale','report_xlsx','crm','product'],
    'data': [
       'security/ir.model.access.csv',
        'views/views.xml',
        'views/actifs.xml',
        'views/shz_livraison.xml',
        'views/suspension.xml',
        'views/preparation.xml',
        'views/commande_sac.xml',
        'views/livraison.xml',
        'views/sacs.xml',
        'views/non_planifie.xml',
        'wizard/wizard_rapport.xml',
        'report/livraison_report.xml',
        'report/livraison_template.xml',
        'views/payment.xml',
        'views/fiche_consultation.xml',
        'views/crm.xml',
    ],
}