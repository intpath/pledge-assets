# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

""" main record (pledge) class """

class Pledge_pledge(models.Model):
    _name = 'pledge.pledge'
    _rec_name = "name"
    _inherit='mail.thread'


    partner_id = fields.Many2one("res.partner",string="Partner/Customer",required=True,readonly=False)
    bid_ref = fields.Char(string="Bid Reference")
    # alert_date = fields.Date(string="Alert date")
    acceptance_date = fields.Date(string="Acceptance date")
    STATES = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('expired', 'Expired'),('cleared','Cleared')
    ]
    status = fields.Selection(STATES, default=STATES[0][0],readonly=True)
    issuing_bank_name =fields.Many2one("pledge.bank",required=True)
    issuing_bank_ref = fields.Char(string="LC Number")
    notes = fields.Text()
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    name=fields.Char(store=True,compute="calc_name")
    lca_type = fields.Selection([('bid bond', 'Bid Bond'),('performance bond','Performance Bond'),('letter of credit','Letter of Credit')],string="Pledge Type") #main document type
    payment_method = fields.Char(string="Payment Method")
    currency_id = fields.Many2one('res.currency', string='Currency') 
    amount = fields.Monetary(string="Amount")
    paid_amount = fields.Monetary(string="Paid Amount")
    benefeciary_bank = fields.Many2one("pledge.bank",string="Benefeciary Bank")
    validity_lines = fields.One2many("pledge.extension","conn",string="Validity/Extension")
    lc_type =fields.Selection([('irrevocable', 'Irrevocable'),('confirmed','Confirmed'),('transferable','Transferable')],string="Letter of Credit Type") # if lc, what lc type
    related_contract = fields.Many2one("contract.contract",string="Related Contract")
    parent_pledge =fields.Many2one('pledge.pledge',string="Parent Pledge")
    latest_date_of_shipment = fields.Date(string="Latest date of shipment")
    expense_lines = fields.One2many("pledge.expense","conn",string="Expense Lines")

    clearance_amount = fields.Integer(string="Clearance Amount")
    clearance_attachement = fields.Binary(string='Attachments')


    def unlink(self):
        for record in self:
            if record.status != "draft":
                raise UserError (_("You cannot delete a confirmed record"))
            res = super(Pledge_pledge,self).unlink()
            return res

    def deduct(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'view_tree_label_picking',
            'view_type': 'form',
            'view_mode':'form',
            'res_model': 'pledge.pledge', 
            'context': {'default_parent_pledge':self.id},
            'target': 'new',
            }

    @api.model
    def create(self,vals):
        res = super(Pledge_pledge,self).create(vals)
        if res.parent_pledge:
            res.parent_pledge.status = "cleared"
        return res

    def reset_draft(self):
        self.status = "draft"

    def re_confirm(self):
        self.status = "confirmed"

    @api.constrains("partner_id","issuing_bank_name")
    def calc_name(self):
        self.name =self.partner_id.name + "-" +self.issuing_bank_name.bank_name+"-"+str(self.id)
    
    def confirm(self):
        self.status = "confirmed"

    def clear_lc(self):
        if self.clearance_amount != 0 and self.clearance_attachement:
            self.status = "cleared"
        else:
            raise UserError (_("Please fill out clearance amount and attach clearence document"))

    # Scheduled Action function
    def proactive_expiration_notification(self):
        today = datetime.date.today()
        pt = int(self.env['ir.config_parameter'].sudo().get_param('pledge_assets.pt') )
        pledges = self.env["pledge.pledge"].search([("status", "=", 'confirmed')])
        for pledge in pledges:
            try:
                if pledge.validity_lines:
                    for validity_line in pledge.validity_lines[0]:
                        delta = ( validity_line.expiration_date - today )
                        if delta.days <= pt and delta.days > 0:
                            self.notify(record=pledge, status="about to expire")
                        elif delta.days <= 0:
                            self.notify(record=pledge, status="expired")
                            pledge.status="expired"
            except Exception as e:
                self.notify(record=pledge, status=str(e))


    def notify(self, record, status):
        channel_id = self.env['mail.channel'].search([('name', '=', 'PledgesNotification')])

        if not channel_id:
            channel_id = self.env['mail.channel'].create({
                'name': 'PledgesNotification',
            })
        
        notification = (
            '<div class="pledge.pledge"><a href="#" class="o_redirect" data-oe-model = "pledge.pledge" data-oe-id="%i">%s</a></div>') % (record.id, record.name)
        
        channel_id.message_post(
            body='Automated Message :Pledge is '+ status + ' ' + notification,
            message_type='comment',
            subtype_id=self.env.ref('mail.mt_comment').id,
            partner_ids=[partner_id.id for partner_id in channel_id.channel_partner_ids])


class Pledge_bank(models.Model):
    _name="pledge.bank"
    _rec_name = 'bank_name'
    bank_name = fields.Char(string="Issuing bank name")


class Pledge_validity(models.Model):
    _name="pledge.extension"
    _order="expiration_date desc"
    
    conn=fields.Integer()
    issuing_date = fields.Date(string="Issuing date",required=True)
    expiration_date = fields.Date(string="Expiration date",required=True)
    

class PledgePartner(models.Model):
    _inherit = "res.partner"

    pledge_count = fields.Integer("Pledges", compute='_compute_pledges', groups="pledge_assets.pledge_user")

    def pledge_partner_re(self):
        return {
            "name": "Pledges",
            "type": "ir.actions.act_window",
            "res_model": "pledge.pledge",
            "views": [[False, "list"],[False, "kanban"], [False, "form"], 
            [False, "graph"], [False, "pivot"], [False, "activity"]],
            "domain": [['partner_id', '=', self.id]],
        }


    def _compute_pledges(self):
        for partner in self:
            operator = 'child_of' if partner.is_company else '='  # the opportunity count should counts the opportunities of this company and all its contacts
            partner.pledge_count = self.env['pledge.pledge'].search_count([('partner_id', operator, partner.id)])


class PledgeExpenses(models.Model):
    _name="pledge.expense"

    conn = fields.Integer()
    name=fields.Many2one("pledge.expensenames",string="Expense Names")
    amount = fields.Float(string="Amount")
    currency = fields.Many2one("res.currency",string="Currency")


class PledgeExpensesNames(models.Model):
    _name="pledge.expensenames"
    _rec_name = "name"

    name = fields.Char(string="Expense Name")
