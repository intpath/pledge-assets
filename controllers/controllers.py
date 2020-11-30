# -*- coding: utf-8 -*-
# from odoo import http


# class LcAlitkan(http.Controller):
#     @http.route('/pledge_assets/pledge_assets/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pledge_assets/pledge_assets/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pledge_assets.listing', {
#             'root': '/pledge_assets/pledge_assets',
#             'objects': http.request.env['pledge.pledge'].search([]),
#         })

#     @http.route('/pledge_assets/pledge_assets/objects/<model("pledge.pledge"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pledge_assets.object', {
#             'object': obj
#         })
