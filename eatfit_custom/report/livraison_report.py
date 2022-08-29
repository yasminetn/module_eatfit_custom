# -*- coding: utf-8 -*-

import json

from odoo import api, models, _
from odoo.tools import float_round
from odoo.exceptions import UserError


class RapportLivraisonReport(models.AbstractModel):
    _name = "report.eatfit_custom.livraison_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        filter = [('etats', '=', 'actif'), ('sale_id.state', '=', 'sale')]
        filter.append(('livraison', '<=', docs.end_date))
        filter.append(('livraison', '>=', docs.start_date))

        if docs.livraison_type:
            filter.append(('livraison_type', '=', docs.livraison_type))

        if docs.livraison_mode:
            filter.append(('livraison_mode', '=', docs.livraison_mode))


        if docs.zone:
            filter.append(('partner_zone', '=', docs.zone))

        if docs.livreur:
            filter.append(('partner_livreur', '=', docs.livreur.id))
            filter_livreur = [('etat', '=', 'en_cours'), ('livreur', '=', docs.livreur.id)]
            recouvrements = self.env['shz.recouvrement'].search(filter_livreur)
        else:
            recouvrements = []

        livraisons = self.env['eatfit.actifs'].search(filter,
                                                      order="sequence,livraison,partner_zone,livraison_type,livraison_mode,partner_livreur,sale_id")

        if livraisons or recouvrements:
            return {
                'docs': docs,
                'livraisons': livraisons,
                'recouvrements': recouvrements,

            }
        else:
            raise UserError("Il n'y a pas ni  livraisons ni Recouvrements  !")


class RapportCommandeReport(models.AbstractModel):
    _name = "report.eatfit_custom.commande_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        filter = [('etats', '=', 'actif'), ('sale_id.state', '=', 'sale')]
        filter.append(('preparation', '<=', docs.end_date))
        filter.append(('preparation', '>=', docs.start_date))

        if docs.livraison_type:
            filter.append(('livraison_type', '=', docs.livraison_type))

        if docs.livraison_mode:
            filter.append(('livraison_mode', '=', docs.livraison_mode))

        if docs.zone:
            filter.append(('partner_zone', '=', docs.zone))

        if docs.calorie:
            filter.append(('partner_calorie', '=', docs.calorie))

        commandes = self.env['eatfit.actifs'].search(filter,
                                                     order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")

        if commandes:
            return {
                'docs': docs,
                'livraisons': commandes,
            }
        else:
            raise UserError("Il n'y a pas Des Commandes !")


class RapportcommandeexigenceReport(models.AbstractModel):
    _name = "report.eatfit_custom.exigence_report"

    @api.model
    def _get_report_values(self, docids, data=None):

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        filter = [('etats', '=', 'actif'), ('sale_id.state', '=', 'sale')]
        filter.append(('preparation', '<=', docs.end_date))
        filter.append(('preparation', '>=', docs.start_date))
        filter.append(('partner_cat', '!=', False))

        if docs.calorie:
            filter.append(('partner_calorie', '=', docs.calorie))

        commandes = self.env['eatfit.actifs'].search(filter, order="partner_calorie,sale_id desc")

        # for rec in commandes:
        #     print([i.name for i in rec.sale_id.partner_id.category_id])
        #     # for s in rec.partner_tags:
        #     #     print(s.name)

        if commandes:
            return {
                'docs': docs,
                'livraisons': commandes,
            }
        else:
            raise UserError("Il n'y a pas Des Exigences!")


class RapportetiquetteReport(models.AbstractModel):
    _name = 'report.module_name.report_name'
    _inherit = 'report.report_xlsx.abstract'

    def samedi(self, data):
        if data == True:
            return '6/7'
        else:
            return '5/7'

    def livraison_type(self, data):
        if data == 'out':
            return 'Livraison'
        else:
            return 'Pickup'

    def generate_xlsx_report(self, workbook, data, lines):

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        filter = [('etats', '=', 'actif'), ('sale_id.state', '=', 'sale')]
        filter.append(('preparation', '<=', docs.end_date))
        filter.append(('preparation', '>=', docs.start_date))

        # Classique
        classiq450 = self.env['eatfit.actifs'].search(
            filter + [('partner_repas', 'ilike', '%Repas Classique 450kcal%')],
            order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")
        classiq600 = self.env['eatfit.actifs'].search(
            filter + [('partner_repas', 'ilike', '%Repas Classique 600kcal%')],
            order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")
        classiq750 = self.env['eatfit.actifs'].search(
            filter + [('partner_repas', 'ilike', '%Repas Classique 750kcal%')],
            order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")
        classiqkids = self.env['eatfit.actifs'].search(filter + [('partner_repas', 'ilike', '%Repas Classique Kids%')],
                                                       order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")

        # Premium
        premium450 = self.env['eatfit.actifs'].search(filter + [('partner_repas', 'ilike', '%Repas Premium 450kcal%')],
                                                      order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")
        premium600 = self.env['eatfit.actifs'].search(filter + [('partner_repas', 'ilike', '%Repas Premium 600kcal%')],
                                                      order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")
        premium750 = self.env['eatfit.actifs'].search(filter + [('partner_repas', 'ilike', '%Repas Premium 750kcal%')],
                                                      order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")
        premiumkids = self.env['eatfit.actifs'].search(filter + [('partner_repas', 'ilike', '%Repas Premium Kids%')],
                                                       order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")

        # petitdej
        petit450 = self.env['eatfit.actifs'].search(filter + [('partner_repas', 'ilike', '%Petit Déjeuner 450kcal%')],
                                                    order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")
        petit600 = self.env['eatfit.actifs'].search(filter + [('partner_repas', 'ilike', '%Petit Déjeuner 600kcal%')],
                                                    order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")
        petit750 = self.env['eatfit.actifs'].search(filter + [('partner_repas', 'ilike', '%Petit Déjeuner 750kcal%')],
                                                    order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")
        petitkids = self.env['eatfit.actifs'].search(filter + [('partner_repas', 'ilike', '%Petit Déjeuner Kids%')],
                                                     order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")

        # gourmet
        gourmet200 = self.env['eatfit.actifs'].search(filter + [('partner_repas', 'ilike', '%Gourmet Light 200kcal%')],
                                                      order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")
        gourmet300 = self.env['eatfit.actifs'].search(filter + [('partner_repas', 'ilike', '%Gourmet 300kcal%')],
                                                      order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")

        commandes = self.env['eatfit.actifs'].search(filter,
                                                     order="partner_calorie,livraison_mode desc,partner_zone,sale_id desc")

        sheet1 = workbook.add_worksheet('Repas classique')
        sheet2 = workbook.add_worksheet('Premium')
        sheet3 = workbook.add_worksheet('Petit dej')
        sheet4 = workbook.add_worksheet('Snacks')
        sheet5 = workbook.add_worksheet('Nom')

        # Classique
        sheet1.write(0, 0, 'Kcal')
        sheet1.write(0, 1, 'Horaire')
        sheet1.write(0, 2, 'Zone')
        sheet1.write(0, 3, 'Client')
        row = 1
        for data in classiq450:
            sheet1.write(row, 0, '450')
            sheet1.write(row, 1, data.livraison_mode)
            sheet1.write(row, 2, data.partner_zone)
            sheet1.write(row, 3, data.partner_name)
            row += 1

        for data in classiq600:
            sheet1.write(row, 0, '600')
            sheet1.write(row, 1, data.livraison_mode)
            sheet1.write(row, 2, data.partner_zone)
            sheet1.write(row, 3, data.partner_name)
            row += 1

        for data in classiq750:
            sheet1.write(row, 0, '750')
            sheet1.write(row, 1, data.livraison_mode)
            sheet1.write(row, 2, data.partner_zone)
            sheet1.write(row, 3, data.partner_name)
            row += 1

        for data in classiqkids:
            sheet1.write(row, 0, 'kids')
            sheet1.write(row, 1, data.livraison_mode)
            sheet1.write(row, 2, data.partner_zone)
            sheet1.write(row, 3, data.partner_name)
            row += 1

        # Premium
        sheet2.write(0, 0, 'Kcal')
        sheet2.write(0, 1, 'Horaire')
        sheet2.write(0, 2, 'Zone')
        sheet2.write(0, 3, 'Client')
        row = 1
        for data in premium450:
            sheet2.write(row, 0, '450')
            sheet2.write(row, 1, data.livraison_mode)
            sheet2.write(row, 2, data.partner_zone)
            sheet2.write(row, 3, data.partner_name)
            row += 1

        for data in premium600:
            sheet2.write(row, 0, '600')
            sheet2.write(row, 1, data.livraison_mode)
            sheet2.write(row, 2, data.partner_zone)
            sheet2.write(row, 3, data.partner_name)
            row += 1

        for data in premium750:
            sheet2.write(row, 0, '750')
            sheet2.write(row, 1, data.livraison_mode)
            sheet2.write(row, 2, data.partner_zone)
            sheet2.write(row, 3, data.partner_name)
            row += 1

        for data in premiumkids:
            sheet2.write(row, 0, 'kids')
            sheet2.write(row, 1, data.livraison_mode)
            sheet2.write(row, 2, data.partner_zone)
            sheet2.write(row, 3, data.partner_name)
            row += 1

        # petitdej
        sheet3.write(0, 0, 'Kcal')
        sheet3.write(0, 1, 'Horaire')
        sheet3.write(0, 2, 'Zone')
        sheet3.write(0, 3, 'Client')
        row = 1
        for data in petit450:
            sheet3.write(row, 0, '450')
            sheet3.write(row, 1, data.livraison_mode)
            sheet3.write(row, 2, data.partner_zone)
            sheet3.write(row, 3, data.partner_name)
            row += 1

        for data in petit600:
            sheet3.write(row, 0, '600')
            sheet3.write(row, 1, data.livraison_mode)
            sheet3.write(row, 2, data.partner_zone)
            sheet3.write(row, 3, data.partner_name)
            row += 1

        for data in petit750:
            sheet3.write(row, 0, '750')
            sheet3.write(row, 1, data.livraison_mode)
            sheet3.write(row, 2, data.partner_zone)
            sheet3.write(row, 3, data.partner_name)
            row += 1

        for data in petitkids:
            sheet3.write(row, 0, 'kids')
            sheet3.write(row, 1, data.livraison_mode)
            sheet3.write(row, 2, data.partner_zone)
            sheet3.write(row, 3, data.partner_name)
            row += 1

        # gourmet
        sheet4.write(0, 0, 'Kcal')
        sheet4.write(0, 1, 'Horaire')
        sheet4.write(0, 2, 'Zone')
        sheet4.write(0, 3, 'Client')
        row = 1
        for data in gourmet200:
            sheet4.write(row, 0, '200')
            sheet4.write(row, 1, data.livraison_mode)
            sheet4.write(row, 2, data.partner_zone)
            sheet4.write(row, 3, data.partner_name)
            row += 1

        for data in gourmet300:
            sheet4.write(row, 0, '300')
            sheet4.write(row, 1, data.livraison_mode)
            sheet4.write(row, 2, data.partner_zone)
            sheet4.write(row, 3, data.partner_name)
            row += 1

        # Sheet Nom
        sheet5.write(0, 0, 'Kcal')
        sheet5.write(0, 1, 'Horaire')
        sheet5.write(0, 2, 'Zone')
        sheet5.write(0, 3, 'Client')
        sheet5.write(0, 4, 'Mode')
        sheet5.write(0, 5, '5/7 ou 6/7')

        row = 1
        for data in commandes:
            sheet5.write(row, 0, data.partner_calorie)
            sheet5.write(row, 1, data.livraison_mode)
            sheet5.write(row, 2, data.partner_zone)
            sheet5.write(row, 3, data.partner_name)
            sheet5.write(row, 4, self.livraison_type(data.livraison_type))
            sheet5.write(row, 5, self.samedi(data.samedi))
            row += 1
