# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _name = "eatfit.report"
    _description = "Sales Analysis Report"
    _auto = False

    _order = 'livraison_mode'

    name = fields.Char('Commande N°', readonly=True)
    date_creation = fields.Date('Date de l\'abonnement', readonly=True)
    date_debut = fields.Date('Date début de l\'abonnement', readonly=True)
    date_fin = fields.Date('Date fin de l\'abonnement' , readonly=True)
    preparation = fields.Date('Date Préparation', readonly=True)
    livraison = fields.Date('Date Livraison', readonly=True)
    product_id = fields.Many2one('product.product', 'Produit', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Client', readonly=True)
    partner_name = fields.Char()
    product_name = fields.Char()
    livraison_mode = fields.Selection([
        ('matin', 'Matin'),
        ('soir', 'Soir')] , string="Horaire")

    horaire = fields.Selection([
        ('matin', 'Matin'),
        ('soir', 'Soir')] , string="Horaire")

    horaire2 = fields.Char()


    etats = fields.Selection([
        ('actif', 'Actif'),
        ('suspension', 'En suspension')], string='Etat')
    etats_commande = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Etat Commande')

    repat = fields.Boolean('repat')
    calorie = fields.Selection([('450', '450'), ('600', '600'), ('750', '750')], string="Calories")

    zone = fields.Selection([('a', 'Zone A'), ('b', 'Zone B'),('pickup', 'Pickup'),('crossfit', 'CrossFit')], string="Zone")

    livraison_type = fields.Selection([
        ('in', 'Pickup'),
        ('out', 'Livraison')], string='Modes de livraison')

    samedi = fields.Boolean(string="6/7")

    order_id = fields.Float()



    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            min(l.id) as id,
            l.product_id as product_id,
             count(*) as nbr,
            s.name as name,
            s.date_creation as date_creation,
            s.date_debut as date_debut,
            s.date_fin as date_fin,
            t.repat as repat,
            t.name as product_name,
            s.partner_id as partner_id,
            s.user_id as user_id,
            s.campaign_id as campaign_id,
             s.team_id as team_id,
             s.state as etats_commande, 
             
             s.livraison_type as livraison_type, 
             s.samedi as samedi, 
                   
             partner.industry_id as industry_id,
             partner.calorie as calorie,
       
             partner.zone as zone,
             partner.name as partner_name,             
             s.id as order_id,
             actifs.preparation as preparation,
             actifs.livraison as livraison,
             actifs.livraison_mode as livraison_mode,
             actifs.livraison_mode as horaire,
             actifs.livraison_mode as horaire2,
             actifs.etats as etats
        """
        for field in fields.values():
            select_ += field

        from_ = """
                sale_order_line l
                  join sale_order s on (l.order_id=s.id)
                left join eatfit_actifs actifs on s.id = actifs.sale_id  
                  join res_partner partner on s.partner_id = partner.id
                  
                   left join product_product p on (l.product_id=p.id)
            left join product_template t on (p.product_tmpl_id=t.id)
                %s
        """ % from_clause

        groupby_ = """
            l.product_id,
            l.order_id,
            s.name,
            s.date_creation,
            s.date_debut,
            s.date_fin,
            s.partner_id,
            s.user_id,
            s.state,    
             s.livraison_type, 
             s.samedi, 
            partner.industry_id,
            partner.calorie,
            partner.zone,
            partner.name,
            actifs.preparation,
            actifs.livraison,
            actifs.livraison_mode,
            actifs.etats,
            t.repat,
            t.name,
            s.id %s
        """ % (groupby)


        return '%s (SELECT %s FROM %s WHERE l.product_id IS NOT NULL GROUP BY %s)' % (with_, select_, from_, groupby_)
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))