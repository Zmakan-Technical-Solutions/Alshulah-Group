# -*- coding: utf-8 -*-
from odoo import http

# class HrPayrollLocalization(http.Controller):
#     @http.route('/hr_payroll_localization/hr_payroll_localization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_payroll_localization/hr_payroll_localization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_payroll_localization.listing', {
#             'root': '/hr_payroll_localization/hr_payroll_localization',
#             'objects': http.request.env['hr_payroll_localization.hr_payroll_localization'].search([]),
#         })

#     @http.route('/hr_payroll_localization/hr_payroll_localization/objects/<model("hr_payroll_localization.hr_payroll_localization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_payroll_localization.object', {
#             'object': obj
#         })