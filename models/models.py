# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

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
    issuing_bank_ref = fields.Char(string="Issuing Bank Reference")
    notes = fields.Text()
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    name=fields.Char(store=True,compute="calc_name")
    lca_type = fields.Selection([('bid bond', 'Bid Bond'),('performance bond','Performance Bond'),('letter of credit','Letter of Credit')],string="Pledge Type")
    payment_method = fields.Selection([('cash', 'Cash'),('bank','Bank')]) 
    amount = fields.Float(string="Amount")
    validity_lines = fields.One2many("pledge.extension","conn",string="Validity/Extension",required=True)
    lc_type =fields.Selection([('customer', 'Customer LC'),('vendor','Vendor LC')],string="Letter of Credit Type")
    
    def re_confirm(self):

        self.status = "confirmed"


    @api.constrains("partner_id","issuing_bank_name")
    def calc_name(self):
        self.name =self.partner_id.name + "-" +self.issuing_bank_name.bank_name+"-"+str(self.id)
    
    def confirm(self):
        self.status = "confirmed"

    def clear_lc(self):
        self.status = "cleared"

    
    def proactive_expiration_notification(self):
        today = datetime.date.today()
        pt = int(self.env['ir.config_parameter'].sudo().get_param('pledge_assets.pt') )
        pledges = self.env["pledge.pledge"].search([("status","=",'confirmed')])
        for pledge in pledges:
            try:
                for validity_line in pledge.validity_lines[0]:
                    delta = ( validity_line.expiration_date - today )
                    if delta.days <= pt and delta.days > 0:
                        self.notify(rec_id=pledge.id,rec_name=pledge.name,status="about to expire")
                    elif delta.days <= 0:
                        self.notify(rec_id=pledge.id,rec_name=pledge.name,status="expired")
                        pledge.status="expired"

            except Exception as e:
                self.notify(rec_id=pledge.id,rec_name=pledge.name,status=str(e))



    def notify(self,rec_id="",rec_name="",status=""): #takes in record_id and record_name
        try:
            channel_id = self.env['mail.channel'].search([('name', '=', 'PledgesNotification')])
            
            notification = ('<div class="pledge.pledge"><a href="#" class="o_redirect" data-oe-model = "pledge.pledge" data-oe-id="%s">#%s</a></div>') % (rec_id, rec_name,)
            channel_id.message_post(
                        body='Automated Message :Pledge is '+ status + " " +notification ,
                        subtype='mail.mt_comment')
        except:
            raise UserError(_("Unable to send Notification,Please check channel Name"))    



class Pledge_bank(models.Model):
    _name="pledge.bank"
    _rec_name = 'bank_name'
    bank_name = fields.Char(string="Issuing bank name")
    



class Pledge_validity(models.Model):

    _name="pledge.extension"

    conn=fields.Integer()
    issuing_date = fields.Date(string="Issuing date")
    expiration_date = fields.Date(string="Expiration date")
    

class PledgePartner(models.Model):

    _inherit = "res.partner"

    pledges_ids = fields.One2many("pledge.pledge","partner_id",string="Pledges")