# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.osv import osv
from datetime import date, timedelta
import odoo.exceptions


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # priority_etoil = fields.Selection(related="partner_id.priority_etoil")

    def shz_note(self):
        partner_ids = [rec.partner_id.id for rec in self]
        return {'type': 'ir.actions.act_window',
                'name': _('Creé Note'),
                'res_model': 'sale.note',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_partner_ids': [(6, 0, partner_ids)],
                            'default_sale_ids': [(6, 0, self.ids)]}}

    def shz_recouvrement(self):
        return {
            'name': _("Convert BC to recouvrement"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'sale.recouvrement',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_sale_recouvrement_line': [(0, 0, {
                    'client': rec.partner_id.id,
                    'order': rec.id,
                    # 'mobile': rec.partner_id.mobile,
                    # 'zone': rec.zone,
                    # 'ville': rec.partner_id.city,
                    # 'adresse': rec.partner_id.street,
                    # 'total_montant_du': rec.order.montant_du,
                    # 'total_sac_rendu': rec.total_sac_rendu,
                    # 'total_bleu_rendu': rec.total_bleu_rendu,
                    # 'horaire': rec.livraison_mode,
                    'etat': 'en_cours',
                    'sale_recouvrement': rec.id
                }) for rec in self]}
        }


class SaleNote(models.TransientModel):
    _name = "sale.note"

    sale_ids = fields.Many2many("sale.order", string="Sales")
    partner_ids = fields.Many2many(comodel_name="res.partner", string="Clients")
    note = fields.Text(string="Note Livraison")
    choix_note = fields.Selection([('remplace', 'Remplacer'), ('ajouter', 'Ajouter')], required=True)

    def gen_sale_note(self):
        for record in self.sale_ids:
            if record.actifs:
                for line_actif in record.actifs:
                    if line_actif.preparation > date.today():
                        print(line_actif.preparation, 'line_actif.preparation')
                        print(date.today(), 'datetime.today()')
                        if self.choix_note == 'ajouter':
                            line_actif.sudo().write({'note': self.note})
                        else:
                            note = str(line_actif.note + ' ' + self.note) if line_actif.note else self.note
                            line_actif.sudo().write({'note': note})

            #
            #
            # # if record.total_amount < record.advance_amount or record.advance_amount == 0.00:
            #
            # note_id = self.env['eatfit.actifs'].create(note_data)
            # # note_id.post()


class Recouvrement(models.Model):
    _name = "shz.recouvrement"

    client = fields.Many2one("res.partner", string="Client")
    order = fields.Many2one("sale.order", string="Bon de commande")
    livreur = fields.Many2one("eatfit.livreur", string="Livreur")
    # mobile = fields.Char(string="Mobile")
    note = fields.Char(string="Note")
    # zone = fields.Selection([('a', 'Zone A'), ('b', 'Zone B'), ('pickup', 'Pickup'), ('crossfit', 'CrossFit')],string="Zone")
    # ville = fields.Char(string="Ville")
    # adresse = fields.Char(string="Adresse")
    # total_montant_du = fields.Float(string="Total Montant du")
    total_sac_rendu = fields.Integer(related="client.total_sac_rendu")
    total_bleu_rendu = fields.Integer(related="client.total_bleu_rendu")
    mobile = fields.Char(related="client.mobile")
    zone = fields.Selection(related="client.zone")
    ville = fields.Char(related="client.city")
    adresse = fields.Char(related="client.street")
    total_montant_du = fields.Float(related="order.montant_du")
    horaire = fields.Selection(related="order.livraison_mode")
    # horaire = fields.Selection([('matin', 'Matin'), ('soir', 'Soir')])
    etat = fields.Selection([('en_cours', 'En cours'), ('suspendu', 'Suspendu'), ('fait', 'Fait')])


class SaleRecouvrement(models.TransientModel):
    _name = "sale.recouvrement"

    livreur = fields.Many2one("eatfit.livreur", string="Livreur", required="True")
    note = fields.Char(string="Note")

    sale_recouvrement_line = fields.One2many(comodel_name="sale.recouvrement.line", inverse_name="sale_recouvrement",
                                             string="Recouvrement lines",
                                             required=False)

    def create_recouvrement(self):
        for rec in self.sale_recouvrement_line:
            vals = {
                'client': rec.client.id,
                'livreur': self.livreur.id,
                'note': self.note,
                'mobile': rec.mobile,
                'zone': rec.zone,
                'ville': rec.ville,
                'adresse': rec.adresse,
                'horaire': rec.horaire,
                'order': rec.order.id,
                'total_montant_du': rec.total_montant_du,
                'total_sac_rendu': rec.total_sac_rendu,
                'total_bleu_rendu': rec.total_bleu_rendu,
                'etat': 'en_cours',
            }

            print(vals)

            record = self.env['shz.recouvrement'].search([('client', '=', rec.client.id)])

            if record['client'].id:
                record.sudo().write(vals)
            else:
                self.env['shz.recouvrement'].create(vals)


class SaleRecouvrementLine(models.TransientModel):
    _name = "sale.recouvrement.line"
    client = fields.Many2one("res.partner", string="Client")
    order = fields.Many2one("sale.order", string="order")
    livreur = fields.Many2one("eatfit.livreur", string="Livreur")
    mobile = fields.Char(string="Mobile")
    note = fields.Char(string="Note")
    zone = fields.Selection([('a', 'Zone A'), ('b', 'Zone B'), ('pickup', 'Pickup'), ('crossfit', 'CrossFit')],
                            string="Zone")
    ville = fields.Char(string="Ville")
    adresse = fields.Char(string="Adresse")
    total_montant_du = fields.Float(string="Total Montant du")
    total_sac_rendu = fields.Integer("Sacs Non Rendu")
    total_bleu_rendu = fields.Integer("Bleu Non Rendu")
    horaire = fields.Selection([('matin', 'Matin'), ('soir', 'Soir')])
    etat = fields.Selection([('en_cours', 'En cours'), ('suspendu', 'Suspendu'), ('fait', 'Fait')])
    sale_recouvrement = fields.Many2one(comodel_name="sale.recouvrement", string="", required=False)
