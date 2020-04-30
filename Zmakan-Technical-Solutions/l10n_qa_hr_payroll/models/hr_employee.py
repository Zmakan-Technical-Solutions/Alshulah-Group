# -*- coding: utf-8 -*-


from odoo import fields, models, api

@api.model
def _lang_get(self):
	return self.env['res.lang'].get_installed()

# add the field language in employee
class HrEmployee(models.Model):
	_inherit='hr.employee'
	_description = "employee additional fields"

	lang = fields.Selection(_lang_get, string='Language', default=lambda self: self.env.lang)
	# name = fields.Char(related='resource_id.name', store=True, oldname='name_related',translate=True, readonly=False)
	job_title = fields.Char("Job Title",translate=True)
	zts_name_arabic = fields.Char(string='Employee')
	zts_joining_date = fields.Date(string='Joining Date')
	zts_qid_number = fields.Char(string='QID Number')
	zts_qid_exp_date = fields.Date(string='QID Expiry')
	zts_passport_exp_date = fields.Date(string='Passport Expiry')
	zts_work_permit_exp_date = fields.Date(string='Work Permit Expiry')
	zts_type = fields.Selection([('cash','Cash'),('trans_bank_card','Transfer To Bank Card'),('trans_bank_ac','Transfer To Bank Account'),('cheque','Cheque')], string='Account Type')
	zts_sponser_name = fields.Many2one('res.partner',string='Sponser')
	zts_member_ids = fields.One2many('member.details', 'zts_member_line_id',string='Member details')	
	zts_personal_email = fields.Char(string='Personal Email')
	zts_personal_phone = fields.Char(string='Personal Phone')
	zts_religion = fields.Many2one('employee.religion',string='Relegion')
	zts_bank_pay = fields.Many2one('res.bank', string='Bank Used To Pay')
	zts_drvng_licns_no = fields.Char(string='Driving Licence Number')
	zts_drvng_licns_issue = fields.Date(string='Driving Licence Issue Date')
	zts_drvng_licns_expry = fields.Date(string='Driving Licence Expiry Date')
	zts_drvng_licns_type = fields.Many2many('license.type',string='Driving Licence Type', translate=True)
	health_card = fields.Char(string='Health Card Number')
	health_card_exp = fields.Date(string='Health Card Expiry Date')
	zts_passport_doc_attachment_id = fields.Many2many('ir.attachment','passport','passport',string="Passport")
	zts_qid_doc_attachment_id = fields.Many2many('ir.attachment','qid', 'qid_col',string="QID")
	zts_lcns_doc_attachment_id = fields.Many2many('ir.attachment','license','lcnse',string="Driving License")
	zts_health_doc_attachment_id = fields.Many2many('ir.attachment','health','health_card',string="Health Card")                                    
	zts_employee_number = fields.Char(string="Staff Number")

class MemberDetails(models.Model):
	_name = 'member.details'
	_description = "employee family member details"

	zts_member_line_id = fields.Many2one('hr.employee',string='Member Details', invisible=True)
	zts_name = fields.Char(string="Name")
	zts_relation_id = fields.Many2one('employee.relation',string='Relation')
	zts_rp_fee_elg = fields.Selection([('eligible','Eligible'),('not','Not Eligible')],string='RP Fees Eligibility')
	zts_health_insurance_elg = fields.Selection([('eligible','Eligible'),('not','Not Eligible')],string='Health Insurance Eligibility')
	zts_ticket_elg = fields.Selection([('eligible','Eligible'),('not','Not Eligible')],string='Ticket Eligibility') 
	zts_religion = fields.Many2one('employee.religion',string='Relegion')
