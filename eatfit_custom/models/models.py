# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.osv import osv
from datetime import date, timedelta
import odoo.exceptions


class ProductTemplate(models.Model):
    _inherit = "product.template"
    repat = fields.Boolean('Un repas ?', default=False)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    actifs = fields.One2many('eatfit.actifs', 'sale_id', auto_join=True, tracking=True)
    montant_du = fields.Float('Montant Du', compute='compute_montant_du')
    samedi = fields.Boolean(string="6/7", tracking=True)
    nb_jours = fields.Integer('Nombre de jours', tracking=True)
    date_creation = fields.Date('Date de l\'abonnement', tracking=True, copy=False)
    date_debut = fields.Date('Début de l\'abonnement', tracking=True, copy=False)
    choix_sac = fields.Selection([('Acheté', 'Acheté'), ('caution', 'Caution')],
                                 store=True, string='Choix du sac', default='Acheté', required=True)
    date_fin = fields.Date('Fin de l\'abonnement', compute='_compute_all', store=True, tracking=True, copy=False)

    historique = fields.One2many(related="partner_id.article_bc")
    historique_refraiche = fields.Boolean(compute="get_historique")

    def compute_montant_du(self):
        for rec in self:
            res = self.env['sale.order'].search(
                [("state", '=', 'sale'), ("partner_id", '=', rec.partner_id.id)])
            rec.montant_du = sum([p.amount_residual for p in res])

    @api.depends('historique')
    def get_historique(self):
        for rec in self:
            rec.partner_id._get_article()
            rec.historique_refraiche = True

    livraison_type = fields.Selection([
        ('in', 'Pickup'),
        ('out', 'Livraison')], string='Modes de livraison', default='out', tracking=True)

    livraison_mode = fields.Selection([
        ('matin', 'Matin'),
        ('soir', 'Soir')], string='Horaire', default='matin', tracking=True)

    nb_jours_actif = fields.Integer('Total jours actif', compute='_compute_all', store=True)
    nb_jours_suspension = fields.Integer('Total jours en suspension', compute='_compute_all', store=True)
    nb_jours_non_planifier = fields.Integer('Total jours  non planifié ', compute='_compute_diff', store=True)

    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice'),
    ], string='Invoice Status', compute='_get_invoice_status_eat', store=False, readonly=True, tracking=True)

    preparation_status = fields.Selection([
        ('actif', 'Actif'),
        ('non_actif', 'Non actif'),
        ('en_suspension', 'En Suspension'),
    ], string='Préparation État', compute='_get_preparation_status_eat', store=False, readonly=True,
        search='_search_state', tracking=True)

    date_preparation_status = fields.Date(string='Actif par date', store=False, readonly=True,
                                          search='_date_search_state', tracking=True)

    bc_preparation_status = fields.Selection([
        ('actif', 'Actif'),
        ('non_actif', 'Non actif'),
    ], string='Préparation État BC', compute='_get_bc_preparation_status_eat', store=False, readonly=True,
        search='_bc_search_state', tracking=True)

    @api.depends('total_sac_rendu', 'total_bleu_rendu', 'sac_acheter',
                 'caution_en_cours')
    def get_total_sac_rendu(self):
        for rec in self:
            # rec.partner_id._get_article()
            rec.partner_id._get_actif_livraison()
            rec.total_sac_rendu_store1 = rec.total_sac_rendu_store = rec.total_sac_rendu
            rec.total_bleu_rendu_store1 = rec.total_bleu_rendu_store = rec.total_bleu_rendu
            rec.sac_acheter_store1 = rec.sac_acheter_store = rec.sac_acheter
            rec.caution_en_cours_store1 = rec.caution_en_cours_store = rec.caution_en_cours

    total_sac_rendu = fields.Integer(related="partner_id.total_sac_rendu")
    total_bleu_rendu = fields.Integer(related="partner_id.total_bleu_rendu")
    sac_acheter = fields.Integer(related="partner_id.sac_acheter")
    caution_en_cours = fields.Integer(related="partner_id.caution_en_cours")

    total_sac_rendu_store = fields.Integer("Sacs Non Rendu store", compute="get_total_sac_rendu")
    total_bleu_rendu_store = fields.Integer("Bleu Non Rendu store", compute="get_total_sac_rendu")
    sac_acheter_store = fields.Integer(string="Sac acheté", compute="get_total_sac_rendu")
    caution_en_cours_store = fields.Integer(string="Caution en cours ", compute="get_total_sac_rendu")

    total_sac_rendu_store1 = fields.Integer("Sacs Non Rendu ", group_operator="avg", store=True)
    total_bleu_rendu_store1 = fields.Integer("Bleu Non Rendu ", group_operator="avg", store=True)
    sac_acheter_store1 = fields.Integer(string="Sac acheté", group_operator="avg", store=True)
    caution_en_cours_store1 = fields.Integer(string="Caution en cours ", group_operator="avg", store=True)

    naissance = fields.Date("Date de naissance", related='partner_id.naissance')
    age = fields.Integer(string="Âge", related='partner_id.age')
    calorie = fields.Selection([('450', '450'), ('600', '600'), ('750', '750')], string="Calories",
                               related='partner_id.calorie')
    zone = fields.Selection(string="Zone", related='partner_id.zone')
    livreur = fields.Many2one('eatfit.livreur', string='Livreur', related='partner_id.livreur')
    # livreur = fields.Many2one('eatfit.livreur', string='Livreur', related='partner_id.livreur')

    objectif = fields.Many2one('eatfit.objectif', string='Objectif')
    formule = fields.Many2one('eatfit.formule', string='Formule')

    @api.onchange('partner_id')
    def get_zone_partner(self):
        if self.partner_id:
            self.zone = self.partner_id.zone
        else:
            self.zone = False

    @api.depends('zone')
    def set_livreur_zone(self):
        if self.zone:
            livreur = self.env['eatfit.livreur'].sudo().search([('zone', '=', self.zone)], limit=1)
            self.livreur = livreur.id
        else:
            self.livreur = False

    def copy(self, default=None):
        default = dict(default or {})
        default['paiement'] = 'not_paid'
        return super().copy(default)

    def _search_state(self, operator, value):
        print('_search_state')
        field_id = self.search([]).filtered(lambda x: x.preparation_status == value)
        return [('id', operator, [x.id for x in field_id] if field_id else False)]

    def _bc_search_state(self, operator, value):
        print('_bc_search_state')
        print('value', value)
        field_id_actifs = self.search([]).filtered(lambda x: x.state == 'sale' and any(
            [a.etats == 'actif' for a in x.actifs if a.preparation == date.today()]))
        clients_actifs = [x.partner_id for x in field_id_actifs]
        if value == 'actif':
            field_id = self.search([]).filtered(lambda x: x.partner_id in clients_actifs)

        else:
            # field_id_nonactif = self.search([]).filtered(
            #     lambda x: x.bc_preparation_status == 'non_actif' and x.state == 'sale' and all(
            #         [a.etats != 'actif' for a in x.actifs]))
            clients_nonactifs = [x for x in self.env['res.partner'].search([]) if x not in clients_actifs]
            field_id = self.search([]).filtered(lambda x: x.partner_id in clients_nonactifs)

        return [('id', operator, [x.id for x in field_id] if field_id else False)]

    def _date_search_state(self, operator, value):
        value = datetime.strptime(value, '%Y-%m-%d').date()
        field_id = self.search([]).filtered(
            lambda x: any([a.preparation == value and a.etats == 'actif' for a in x.actifs]) and x.state == 'sale')
        return [('id', operator, [x.id for x in field_id] if field_id else False)]

    @api.depends('actifs')
    def _get_preparation_status_eat(self):
        for rec in self:
            actifs = rec.actifs.filtered(lambda x: x.preparation == date.today())
            if actifs:
                for act in actifs:

                    if act.etats == 'actif':
                        rec.preparation_status = 'actif'
                    else:
                        rec.preparation_status = 'en_suspension'
            else:
                rec.preparation_status = 'non_actif'

    @api.depends('actifs')
    def _get_date_preparation_status_eat(self):
        for rec in self:
            actifs = rec.actifs.filtered(lambda x: x.preparation == rec.list_preparation)
            if actifs:
                rec.date_preparation_status = 'actif'
            else:
                rec.date_preparation_status = 'non_actif'

    @api.depends('actifs')
    def _get_bc_preparation_status_eat(self):
        for rec in self:
            actifs = rec.actifs.filtered(lambda x: x.preparation == date.today() and x.etats == 'actif')
            if actifs:
                rec.bc_preparation_status = 'actif'
            else:
                rec.bc_preparation_status = 'non_actif'

    @api.depends('order_line.invoice_lines')
    def _get_invoice_status_eat(self):
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(
                lambda r: r.type in ('out_invoice', 'out_refund'))

            # order.invoice_ids = invoices
            order_invoice_count = len(invoices)
            if order_invoice_count > 0:
                order.invoice_status = 'invoiced'
            else:
                order.invoice_status = 'to invoice'

    def calcul_actif(self):
        # Reset Data
        if self.actifs != False:
            self.actifs.unlink()

        # Cheque NB Jours
        if self.nb_jours == 0:
            raise osv.except_osv(('Erreur'), ("Nombre de jours Obligatoire"))

        if self.date_debut == False:
            raise osv.except_osv(('Erreur'), ("Date début de l'abonnement Obligatoire"))

        if self.samedi == True:
            weekdays = [5]
        else:
            weekdays = [5, 4]

        actifs = self.env['eatfit.actifs']

        i = 0
        delta = 0
        while i < self.nb_jours:
            preparation = self.date_debut + timedelta(days=delta)
            if preparation.weekday() in weekdays:
                delta += 1
                continue
            i += 1
            delta += 1

            if preparation.weekday() == 4:
                livraison_mode = 'soir'
            else:
                livraison_mode = self.livraison_mode

            ligne = {
                'sale_id': self.id,
                'livraison_mode': livraison_mode,
                'preparation': preparation,
                'partner_zone': self.zone,
                'partner_livreur': self.livreur.id,
                'livraison_type': self.livraison_type
            }
            actifs.create(ligne)

    @api.depends('actifs', 'nb_jours', 'actifs.etats')
    def _compute_all(self):
        for order in self:
            nb_jours_actif = len(order.actifs.filtered(lambda r: r.etats == 'actif'))
            nb_jours_suspension = len(order.actifs.filtered(lambda r: r.etats == 'suspension'))
            actif_line = order.actifs.filtered(lambda r: r.etats == 'actif').sorted(lambda r: r.preparation)
            if len(actif_line) > 0 and self.date_creation:
                actif_line_last_date = actif_line[-1].preparation
            else:
                actif_line_last_date = False

            order.update({
                'nb_jours_actif': nb_jours_actif,
                'nb_jours_suspension': nb_jours_suspension,
                'date_fin': actif_line_last_date,
            })

            #  Mode and type of livraison
            for line in order.actifs.filtered(lambda r: r.livraison_mode == False):
                line.livraison_type = order.livraison_type
                line.livraison_mode = order.livraison_mode

    @api.depends('actifs', 'nb_jours', 'nb_jours_actif')
    def _compute_diff(self):
        for rec in self:
            rec.nb_jours_non_planifier = rec.nb_jours - rec.nb_jours_actif


class PartnerCustomField(models.Model):
    _inherit = 'res.partner'

    # priority_etoil = fields.Selection([
    #     ('0', 'Normal'),
    #     ('1', 'VIP'), ], default='1')
    naissance = fields.Date("Date de naissance")
    age = fields.Integer(string="Âge", compute="_get_age", store=True)
    actifs_livraison = fields.Integer(string="Total Actifs", compute="_get_actif_livraison", default=0)

    total_sac_rendu = fields.Integer(string="Sacs Non Rendu", compute="_get_actif_livraison", default=0, store=1)
    total_bleu_rendu = fields.Integer(string="Bleus Non Rendu", compute="_get_actif_livraison", default=0, store=1)

    calorie = fields.Selection([('450', '450'), ('600', '600'), ('750', '750')], string="Calories")
    zone = fields.Selection([('a', 'Zone A'), ('b', 'Zone B'), ('pickup', 'Pickup'), ('crossfit', 'CrossFit')],
                            string="Zone")
    # livreur = fields.Many2one('eatfit.livreur', string='Livreur')
    livreur = fields.Many2one('eatfit.livreur', string='Livreur', compute="set_livreur_zone")

    fiche_consultation = fields.One2many('eatfit.consultation', 'partner_id', string='Fiches Consultation')

    objectif = fields.Selection([('Perte de poids', 'Perte de poids'), ('Sèche musculaire', 'Sèche musculaire'),
                                 ('Prise de masse', 'Prise de masse'), ('Bien être', 'Bien être')], string="Objectif")

    genre = fields.Selection([('Male', 'Homme'), ('Female', 'Femme')], string="Genre")
    situation_famil = fields.Selection([('celibataire', 'Celibataire'), ('marie', 'Marié'), ('veuf', 'Veuf')],
                                       string="Situation familiale")
    natinali = fields.Many2one('res.country', string='Nationalité')
    medium = fields.Many2one('utm.medium', string='Moyen')
    club = fields.Many2one('utm.club', string='Club de sport')

    frequence = fields.Selection(
        [('Sédentaire', 'Sédentaire'), ('Modérément actif', 'Modérément actif'), ('Actif', 'Actif'),
         ('Très actif', 'Très actif')],
        string="Fréquence sportive")

    tabac = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Tabac")
    alcol = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Consommation d'alcool")
    sommeil = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Qualité de sommeil")

    maladie = fields.Char("Maladie chronique/métabolique")
    allergie = fields.Char("Allergie et intolérence alimentaires")
    medicaments = fields.Char("Médicaments / Anti-dépresseur")

    menipause = fields.Selection([('oui', 'Oui'), ('non', 'Non')], string="Menipause")

    nb_cal = fields.Float("NB Calorie")
    poids = fields.Float("Poids")
    taille = fields.Float("Taille")

    @api.depends('zone')
    def set_livreur_zone(self):
        if self.zone:
            livreur = self.env['eatfit.livreur'].sudo().search([('zone', '=', self.zone)], limit=1)
            self.livreur = livreur.id
        else:
            self.livreur = False

    def _get_actif_livraison(self):

        for record in self:
            record.actifs_livraison = 0
            record.total_sac_rendu = 0
            record.total_bleu_rendu = 0
            actifs_livraison_ids = self.env['sale.order'].search(
                [("state", '=', 'sale'), ("partner_id", '=', record.id)]).ids
            if len(actifs_livraison_ids) != 0:
                actifs = self.env['eatfit.actifs'].search(
                    [("sale_id", 'in', actifs_livraison_ids), ('etats', '=', 'actif')])
                record.actifs_livraison = len(actifs)
                if len(actifs) > 0:
                    record.total_sac_rendu = record.actifs_livraison - sum([i.sacs for i in actifs])
                    record.total_bleu_rendu = record.actifs_livraison - sum([i.bleus for i in actifs])

        return {

            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # def clean_tree_view_client(self):
    #     recs = self.env['res.partner'].search([])
    #     for rec in recs:
    #         rec._get_actif_livraison()

    sac_acheter = fields.Integer(string="Sac acheté", compute="_get_sac_acheter")
    caution_en_cours = fields.Integer(string="Caution en cours ", compute="_get_caution_en_cours")

    def _get_caution_en_cours(self):
        for record in self:
            res = self.env['sale.order'].search(
                [("state", '=', 'sale'), ("partner_id", '=', record.id), ("choix_sac", '=', 'Caution')])

            sac_iso = sum(
                [line.product_uom_qty for rec in res for line in rec.order_line if
                 line.product_id.name == "Sac Isotherme"])
            retour_sac_iso = sum(
                [line.product_uom_qty for rec in res for line in rec.order_line if
                 line.product_id.name == "Retour Sac Isotherme"])

            result = sac_iso - retour_sac_iso

        self.caution_en_cours = result

    def _get_sac_acheter(self):

        for record in self:
            res = self.env['sale.order'].search(
                [("state", '=', 'sale'), ("partner_id", '=', record.id), ("choix_sac", '=', 'Acheté')])

            sac_iso = sum(
                [line.product_uom_qty for rec in res for line in rec.order_line if
                 line.product_id.name == "Sac Isotherme"])

        self.sac_acheter = sac_iso

    article_bc = fields.One2many('eatfit.rapport.bc', 'partner_id', string="Article BC")
    execute_get_article = fields.Char(compute="_get_article", string="test")

    def _get_article(self):
        res = self.env['sale.order.line'].search(
            ['&', ("state", '=', 'sale'), ("order_partner_id", '=', self.id),
             ("product_id.name", "in", ["Sac Isotherme", "Retour Sac Isotherme"])])
        domain = [('partner_id', '=', self.id)]
        self.env['eatfit.rapport.bc'].search(domain).sudo().unlink()

        for rec in res:
            vals = {
                'partner_id': self.id,
                'reference_bc': rec.order_id.id,
                'date_bc': rec.order_id.date_order,
                'date_last_update': rec.product_id.write_date,
                'article': rec.product_id.name,
                'choix_sac': rec.order_id.choix_sac,
            }
            self.env['eatfit.rapport.bc'].create(vals)

        # self.article_bc = 0
        self.execute_get_article = "tt"

    @api.depends('naissance')
    def _get_age(self):
        for record in self:
            if record.naissance:
                today = date.today()
                record.age = today.year - record.naissance.year - (
                        (today.month, today.day) < (record.naissance.month, record.naissance.day))

    # @api.depends('naissance')
    # def _get_zone_par_default(self):


class eatfitObjectif(models.Model):
    _name = 'eatfit.objectif'
    name = fields.Char('Objectif')


class eatfitFormule(models.Model):
    _name = 'eatfit.formule'
    name = fields.Char('Formule')


class eatfitRapportBc(models.Model):
    _name = 'eatfit.rapport.bc'
    reference_bc = fields.Many2one(comodel_name="sale.order", string="Référence BC")
    partner_id = fields.Many2one(comodel_name="res.partner")
    date_bc = fields.Datetime('Date du BC')
    date_last_update = fields.Datetime('Date Last update')
    choix_sac = fields.Char('Choix du Sac')
    article = fields.Char('Article')


class eatfitlivreur(models.Model):
    _name = 'eatfit.livreur'
    name = fields.Char('Livreur')
    zone = fields.Selection([('a', 'Zone A'), ('b', 'Zone B'), ('pickup', 'Pickup'), ('crossfit', 'CrossFit')],
                            string="Zone")
    sequence = fields.Integer('Sequence')

    _sql_constraints = [
        ('name', 'unique (name)',
         'Livreur exists !')
    ]


class actifs(models.Model):
    _name = 'eatfit.actifs'
    name = fields.Char('Actifs')

    sequence = fields.Integer('Sequence')
    note = fields.Char('Note')
    montant_du = fields.Float('Montant Du', related='sale_id.montant_du')
    aff_montant_du = fields.Boolean(string="Masquer MD")

    preparation = fields.Date('Date Préparation')
    livraison_type = fields.Selection([
        ('in', 'Pickup'),
        ('out', 'Livraison')], string='Modes de livraison')

    livraison_mode = fields.Selection([
        ('matin', 'Matin'),
        ('soir', 'Soir')], string='Horaire')

    etats = fields.Selection([
        ('actif', 'Actif'),
        ('suspension', 'En suspension')], string='Etat', default='actif')

    sale_id = fields.Many2one('sale.order', "Commande N°")
    partner_id = fields.Many2one(string="Client id", related='sale_id.partner_id')
    partner_name = fields.Char(string="Client", related='sale_id.partner_id.name')
    partner_cat = fields.Many2many(string="Client", related='sale_id.partner_id.category_id')
    partner_tags = fields.Char(string="Tags", compute="_get_tags")

    partner_mobile = fields.Char('Mobile', related='sale_id.partner_id.mobile')
    partner_phone = fields.Char('Téléphone', related='sale_id.partner_id.phone')

    # partner_priority = fields.Selection('Priority', related='sale_id.partner_id.priority_etoil')
    # @api.model
    # def _default_zone(self):
    #     self.partner_zone = self.env['sale.order'].browse('zone')

    partner_zone = fields.Selection([('a', 'Zone A'), ('b', 'Zone B'), ('pickup', 'Pickup'), ('crossfit', 'CrossFit')],
                                    string="Zone", )

    # partner_zone = fields.Selection('Zone', related='sale_id.partner_id.zone', store=True)
    partner_calorie = fields.Selection('Calorie', related='sale_id.partner_id.calorie', store=True)

    total_sac_rendu = fields.Integer("Sacs Non Rendu", compute='get_total_sac_rendu')
    total_bleu_rendu = fields.Integer("Bleu Non Rendu", compute='get_total_sac_rendu')
    samedi = fields.Boolean("samedi", related='sale_id.samedi')

    partner_ville = fields.Char('Ville', related='sale_id.partner_id.city')
    partner_Adresse = fields.Char('Adresse', related='sale_id.partner_id.street')
    # partner_livreur = fields.Char('Livreur', related='sale_id.partner_id.livreur.name')
    partner_livreur = fields.Many2one('eatfit.livreur', string='Livreur', store=True)

    @api.onchange('partner_zone')
    def get_livreur(self):

        self.partner_livreur = self.env['eatfit.livreur'].sudo().search([('zone', '=', self.partner_zone)]).id

    partner_repas = fields.Char('Repas', compute="_get_repas", search='_search_repat')
    partner_repas_stored = fields.Char('Repas', compute="_get_repas", store=True)

    livraison = fields.Date('Date Livraison', compute="_get_livraison", store=True)

    sacs = fields.Integer("Sacs Rendu", default=1)
    bleus = fields.Integer("Bleus", default=1)

    # self.montant_du = montant_du

    @api.depends('total_sac_rendu', 'total_bleu_rendu')
    def get_total_sac_rendu(self):
        for rec in self:
            rec.partner_id._get_actif_livraison()
            rec.total_sac_rendu = rec.partner_id.total_sac_rendu
            rec.total_bleu_rendu = rec.partner_id.total_bleu_rendu

    @api.onchange('preparation', 'livraison_mode')
    @api.depends('preparation', 'livraison_mode')
    def _get_livraison(self):
        for rec in self:
            if rec.livraison_mode == 'matin' and rec.preparation:
                rec.livraison = rec.preparation + timedelta(days=1)
            else:
                rec.livraison = rec.preparation

    def _search_repat(self, operator, operand):
        self._cr.execute("""
        SELECT eatfit_actifs.id as id,product_template.name as product
        FROM eatfit_actifs
        join sale_order ON (eatfit_actifs.sale_id = sale_order.id)
        join sale_order_line ON (sale_order_line.order_id = sale_order.id)
        join product_product ON (sale_order_line.product_id = product_product.id)
        LEFT JOIN product_template ON product_template.id = product_product.product_tmpl_id
        WHERE
        (eatfit_actifs.etats = 'actif') AND (sale_order.state = 'sale') AND (product_template.name ilike %s)
        """, (operand,))

        data = self._cr.dictfetchall()
        ids = [l['id'] for l in data]
        return [('id', 'in', ids)]

    @api.depends('sale_id.order_line')
    def _get_repas(self):
        for rec in self:
            ps = self.env['sale.order.line'].search([('order_id', '=', rec.sale_id.id)]).mapped('product_id').filtered(
                lambda att: att.repat == True).mapped('name')
            rec.partner_repas = '|'.join(ps)

    def _get_tags(self):
        for rec in self:
            tags = [i.name for i in rec.sale_id.partner_id.category_id]
            rec.partner_tags = '|'.join(tags)


class fiche_consultation(models.Model):
    _name = 'eatfit.consultation'

    date = fields.Date('Date')
    taille = fields.Float(string="Taille")
    poids = fields.Float(string="Poids")
    grasse = fields.Float(string="Masse grasse")
    musculaire = fields.Float(string="Masse musculaire")
    tail = fields.Float(string="Tour de taille")
    hanches = fields.Float(string="Tour de hanches")
    circonference = fields.Float(string="Circonférence brachiale")
    partner_id = fields.Many2one('res.partner')
    note = fields.Char('Note')


class club(models.Model):
    _name = 'utm.club'
    name = fields.Char('Club')
