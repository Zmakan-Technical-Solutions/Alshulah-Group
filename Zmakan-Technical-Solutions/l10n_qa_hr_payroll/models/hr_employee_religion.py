# -*- coding: utf-8 -*-

from odoo import fields, models, api

class HrEmployeeReligion(models.Model):
	_name ='employee.religion'
	_description = "employee relegion"
	
	name = fields.Char(string="Religion")