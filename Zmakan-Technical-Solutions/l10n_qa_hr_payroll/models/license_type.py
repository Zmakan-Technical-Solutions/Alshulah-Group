# -*- coding: utf-8 -*-

from odoo import fields, models, api

class LicenseType(models.Model):
	_name ='license.type'
	_description = "Types of licence"

	name = fields.Char(string="License Type")