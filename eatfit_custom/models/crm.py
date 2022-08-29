# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    nb_jours = fields.Integer('NB Jours')
    nb_semaines = fields.Integer('NB Semaines')
    nb_plat = fields.Integer('Nb plat')

    shz_note = fields.Many2one('crm.note', 'Note')

    repas = fields.One2many('crm.repas', 'lead_id', string='Repas')
    collation = fields.One2many('crm.collation', 'lead_id', string='Collations')


class LeadNote(models.Model):
    _name = 'crm.note'
    name = fields.Char('Nom')


class LeadeCollation(models.Model):
    _name = 'crm.collation'
    name = fields.Selection(
        [('Jus Detox et Immunity Shots', 'Jus Detox et Immunity Shots'), ('Fruit et légumes', 'Fruit et légumes'),
         ('Gourmet Light', 'Gourmet Light'), ('Gourmet', 'Gourmet')], string='Nom')
    nbr = fields.Integer('Nb')
    lead_id = fields.Many2one('crm.lead')


class LeadeRepas(models.Model):
    _name = 'crm.repas'
    name = fields.Selection([('Dejeuner', 'Dejeuner'), ('Petit déj', 'Petit déj'), ('Diner', 'Diner')], string='Nom')
    taille = fields.Integer('Taille')
    lead_id = fields.Many2one('crm.lead')
