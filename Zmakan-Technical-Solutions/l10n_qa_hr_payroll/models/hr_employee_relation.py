# -*- coding: utf-8 -*-

from odoo import fields, models, api

class HrEmployeeRelation(models.Model):
	_name ='employee.relation'
	_description = "employee relation"

	name = fields.Char(string="Relation")    
