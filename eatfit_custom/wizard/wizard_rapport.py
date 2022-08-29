from odoo import api, fields, models, _
import time
from datetime import datetime
from dateutil.relativedelta import  relativedelta

class RapportLivraison(models.TransientModel):
    _name = "rapport.livraison"

    start_date = fields.Date(string="Date de début",required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
    end_date =  fields.Date(string="Date de fin",required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
    livraison_type = fields.Selection([
        ('in', 'Pickup'),
        ('out', 'Livraison')], string='Modes de livraison')

    livraison_mode = fields.Selection([
        ('matin', 'Matin'),
        ('soir', 'Soir')], string='Horaire')

    zone = fields.Selection([('a', 'Zone A'), ('b', 'Zone B'),('pickup', 'Pickup'),('crossfit', 'CrossFit')], string="Zone")
    livreur = fields.Many2one('eatfit.livreur', string='Livreur')


    def check_report(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date'])[0])

        return self.env.ref('eatfit_custom.action_livraison_raport').report_action(self, data=data, config=False)
class RapportCommande(models.TransientModel):
    _name = "rapport.commande"

    start_date = fields.Date(string="Date de début",required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
    end_date =  fields.Date(string="Date de fin",required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
    livraison_type = fields.Selection([
        ('in', 'Pickup'),
        ('out', 'Livraison')], string='Modes de livraison')

    livraison_mode = fields.Selection([
        ('matin', 'Matin'),
        ('soir', 'Soir')], string='Horaire')

    zone = fields.Selection([('a', 'Zone A'), ('b', 'Zone B'),('pickup', 'Pickup'),('crossfit', 'CrossFit')], string="Zone")
    calorie = fields.Selection([('450', '450'), ('600', '600'), ('750', '750')], string="Calories",)


    def check_report(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date'])[0])

        return self.env.ref('eatfit_custom.action_commande_raport').report_action(self, data=data, config=False)
class Rapportcommandeexigence(models.TransientModel):
    _name = "rapport.commandeexigence"

    start_date = fields.Date(string="Date de début",required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
    end_date =  fields.Date(string="Date de fin",required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
    calorie = fields.Selection([('450', '450'), ('600', '600'), ('750', '750')], string="Calories",)



    def check_report_ex(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date'])[0])

        return self.env.ref('eatfit_custom.action_commandeexigence_raport').report_action(self, data=data, config=False)

class Rapportetiquette(models.TransientModel):
    _name = "rapport.etiquette"

    start_date = fields.Date(string="Date de début",required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
    end_date =  fields.Date(string="Date de fin",required=True,default=lambda *a: time.strftime('%Y-%m-%d'))



    def check_report(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date'])[0])

        return self.env.ref('eatfit_custom.etquette_xlsx').report_action(self, data=data, config=False)