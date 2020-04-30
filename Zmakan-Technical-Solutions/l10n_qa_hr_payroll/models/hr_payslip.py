# -*- coding: utf-8 -*-

import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval


class HrPayslip(models.Model):
    _inherit='hr.payslip'

    # for checking the employee language is otherthan english, if so then add the employee language translation in the payslip
    def payslip_translation(self, source):
        if self.employee_id.lang:
            trans_id= self.env['ir.translation'].search([('src','=',source),('lang','=',self.employee_id.lang)],limit=1)
            value= trans_id.value
            return value

    @api.model
    def _get_inputs(self):
        res = []
        # input_id = self.env['hr.payslip.input'].search([])
        # raise UserError(str(input_id))
        input_line_ids = self.struct_id.input_line_type_ids
        # raise UserError(str(input_line_ids))
        for inp in input_line_ids:
            input_data = {
                'input_type_id':inp.id,
                'name': inp.name,
                'code': inp.code,
                # 'struct_ids' : self.struct_id
                'contract_id': self.contract_id,
            }
            res += [input_data]
        return res

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id: # Add a default contract if not already defined
            contracts = employee._get_contracts(date_from, date_to)
            # if contracts.structure_type_id.name == 'Base':
            #   structure = self.env['hr.payroll.structure'].search([('type_id','=','Base')])
            #   for struct in structure:
            #       for rule in struct.rule_ids:
            #           if rule.code == 'GROSS':
            #               rule.unlink()
            #           if rule.code == 'NET':
            #               rule.unlink()   
                            # raise UserError(str("stucture"))

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        payslip_name = self.struct_id.payslip_name or _('Salary Slip')
        self.name = '%s - %s - %s' % (payslip_name, self.employee_id.name or '', format_date(self.env, self.date_from, date_format="MMMM y"))

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _("This payslip can be erroneous! Work entries may not be generated for the period from %s to %s." %
                (date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1), date_to))
        else:
            self.warning_message = False

        self.worked_days_line_ids = self._get_new_worked_days_lines()
        input_id = self.env['hr.payslip.input'].search([('payslip_id','=',self.struct_id.id)])
        input_line_ids = self._get_inputs()
        input_lines = self.input_line_ids.browse([])
        # raise UserError(str(input_lines))     
        for r in input_line_ids:
            # raise UserError(str(r))
            input_lines += input_lines.new(r)
            # raise UserError(str(input_lines))         
        self.input_line_ids = input_lines
        # raise UserError(str(input_line_ids))  
        return

class SalaryRule(models.Model):
    _inherit='hr.salary.rule'

    name = fields.Char(required=True,translate=True)
