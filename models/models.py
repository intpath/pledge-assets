# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Pledge_pledge(models.Model):
    _name = 'pledge.pledge'
    _description = 'pledge.pledge'

    partner_id = fields.Many2one("res.partner",string="Partner/Customer")
    issuing_date = fields.Date(string="Issuing date")
    expiration_date = fields.Date(string="Expiration date")
    alert_date = fields.Date(string="Alert date")
    acceptance_date = fields.Date(string="Acceptance date")
    STATES = [
    ('process', 'In Process'),
    ('active', 'Active'),
    ('expired', 'Expired'),
    ]
    status = fields.Selection(STATES, default=STATES[0][0])
    issuing_bank_name =fields.Many2one("pledge.bank")
    issuing_bank_ref = fields.Char(string="Issuing Bank Reference")
    note = fields.Text()
    attachement= fields.Binary(string="Attachement")



    


class Pledge_bank(models.Model):
    _name="pledge.bank"
    _rec_name = 'bank_name'
    bank_name = fields.Char(string="Issuing bank name")
    