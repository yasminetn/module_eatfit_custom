# -*- coding: utf-8 -*-
import json
from odoo import http, _
from odoo.http import request
import logging
import datetime
import urllib.request as urllib2



_logger = logging.getLogger(__name__)


class RestAPI(http.Controller):

    @http.route('/api/sale/', type='http', csrf=False, cros="*", auth="public", methods=['POST'], website=True)
    def create_rig(self, **kw):
        print('ok bb')
        request.session.authenticate(request.session.db, 'boutitinizar@gmail.com', 'Mnb22433')
        data = request.params
        print("data", data)


        team = 1

        # if data["type_consultation"] == "par tel":
        #     team = 8
        # elif data["type_consultation"] == "sur place":
        #     team = 1
        # elif data["type_consultation"] == "par platfrom":
        #     team = 6

        partner = request.env['res.partner'].create({
            'name': data['prenom'] + " " + data['nom'],
            'naissance': data['date'],
            'genre': data['genre'],
            'objectif': data['objectif'],
            'poids': data['poid'],
            'taille': data['taille'],
            'frequence': data['frequence1'],
            'nb_cal': data['kcal'],
            'email': data['mail'],
            'mobile': data['mobile'],
            'street': data['ville'],
        })
        print('partner', partner)

        lead = request.env['crm.lead'].create({
            'name': data['prenom']+" "+data['nom'],
            'email_from': data['mail'],
            'mobile': data['mobile'],
            'city': data['ville'],
        #     'description': data,
            'partner_id': partner.id,
            'team_id': team
        }).sudo()

        lead.update({
            'team_id': team
        })


        # if data.get('formule_infos'):
        #     data_repas = [(0,0,{'name':data.get('formule_infos')['type_repas'][d]['label'],'taille':int(data.get('formule_infos')['taille_repas'][0]['value'])}) for d  in range(len(data.get('formule_infos')['type_repas']))]
        #     data_collation = [(0,0,{'name':data.get('formule_infos')['collation'][d]['label'],'nbr':int(data.get('formule_infos')['nb_collation'][d]['count'])}) for d  in range(len(data.get('formule_infos')['collation']))]
        #     lead.update({
        #         'nb_jours' : data.get('formule_infos')['nb_jours'],
        #         'nb_semaines' : data.get('formule_infos')['nb_semaines'],
        #         'nb_plat' : data.get('formule_infos')['nb_plat'],
        #         'repas' : data_repas,
        #         'collation' : data_collation
        #     })



