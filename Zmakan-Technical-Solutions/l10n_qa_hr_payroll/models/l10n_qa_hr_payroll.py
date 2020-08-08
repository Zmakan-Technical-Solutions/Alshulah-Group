# -*- coding: utf-8 -*-

import logging
import time
import datetime
from datetime import date, datetime, time,timedelta
from datetime import date
from pytz import timezone
from datetime import time as datetime_time
from dateutil import relativedelta
from odoo.tools import float_utils
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
	_inherit='hr.payslip'


	# for calculating unemployment days in payslip
	@api.model
	def _get_worked_day_lines(self):
		"""
		:returns: a list of dict containing the worked days values that should be applied for the given payslip
		"""
		res = []
		# fill only if the contract as a working schedule linked
		self.ensure_one()
		contract = self.contract_id
		if contract.resource_calendar_id:
			paid_amount = self._get_contract_wage()			
			unpaid_work_entry_types = self.struct_id.unpaid_work_entry_type_ids.ids

			work_hours = contract._get_work_hours(self.date_from, self.date_to)
			total_hours = sum(work_hours.values()) or 1
			work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
			
			biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
			add_days_rounding = 0

			contract_day_start = datetime.combine(fields.Date.from_string(contract.date_start), time.min)

			day_from = datetime.combine(fields.Date.from_string(self.date_from), time.min)
			day_to = datetime.combine(fields.Date.from_string(self.date_to), time.max)
			# compute unemployment days
			# for work_entry_type_id, hours in work_hours_ordered:
			# 	work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
			# 	is_paid = work_entry_type_id not in unpaid_work_entry_types
			# 	calendar = contract.resource_calendar_id
			# 	days = round(hours / calendar.hours_per_day, 5) if calendar.hours_per_day else 0
			# 	if work_entry_type_id == biggest_work:
			# 		days += add_days_rounding
			# 	day_rounded = self._round_days(work_entry_type, days)
			# 	add_days_rounding += (days - day_rounded)
			if contract_day_start > day_from and contract.date_end == 0:					
				unemployment_before_contract_details =contract.employee_id._get_work_days_data(day_from,contract_day_start,calendar=contract.resource_calendar_id)
				unemployment_before_contract_details = {
					'work_entry_type_id': self.env.ref('l10n_qa_hr_payroll.work_entry_type_unemployment').id,
					# 'sequence': work_entry_type.sequence,						
					'number_of_days': unemployment_before_contract_details['days'],
					'number_of_hours': unemployment_before_contract_details['hours'],
				}
				res.append(unemployment_before_contract_details)
			if contract.date_end:
				contract_day_end = datetime.combine(fields.Date.from_string(contract.date_end), time.max)
				if contract_day_start > day_from:
					unemployment_before_contract = contract.employee_id._get_work_days_data(day_from, contract_day_start,calendar=contract.resource_calendar_id)
					unemployment_before_contract_details = {
						'work_entry_type_id': self.env.ref('l10n_qa_hr_payroll.work_entry_type_unemployment').id,
						'code': 'Unemployment',
						'number_of_days': unemployment_before_contract['days'],
						'number_of_hours': unemployment_before_contract['hours'],
					}
					if day_to <= contract_day_end:
						res.append(unemployment_before_contract_details)
				if day_to > contract_day_end:
					unemployment_after_contract =contract.employee_id._get_work_days_data(contract_day_end,day_to,calendar=contract.resource_calendar_id)

					unemployment_after_contract_details = {
						'work_entry_type_id': self.env.ref('l10n_qa_hr_payroll.work_entry_type_unemployment').id,
						'code': 'Unemployment',
						'number_of_days': (unemployment_before_contract['days'] + unemployment_after_contract['days']) if contract_day_start > day_from else unemployment_after_contract['days'],
						'number_of_hours': (unemployment_before_contract['hours'] + unemployment_after_contract['hours']) if contract_day_start > day_from else unemployment_after_contract['hours'],
						'contract_id': contract.id,
					}
					res.append(unemployment_after_contract_details)
			for work_entry_type_id, hours in work_hours_ordered:				
				work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
				is_paid = work_entry_type_id not in unpaid_work_entry_types
				calendar = contract.resource_calendar_id
				days = round(hours / calendar.hours_per_day, 5) if calendar.hours_per_day else 0
				# days = hours / calendar.hours_per_day if calendar.hours_per_day else 0
				if work_entry_type_id == biggest_work:
					days += add_days_rounding
				day_rounded = self._round_days(work_entry_type, days)
				add_days_rounding += (days - day_rounded)
				_logger.log(25,'123456666666')
				_logger.log(25,work_entry_type.name)
				attendance_line = {
					'sequence': work_entry_type.sequence,
					'work_entry_type_id': work_entry_type_id,
					'number_of_days': day_rounded,
					'number_of_hours': hours,
					'amount': hours * paid_amount / total_hours if is_paid else 0,
				}
				res.append(attendance_line)
				

			#     # compute leaves
			leaves = {}
			calendar = contract.resource_calendar_id
			tz = timezone(calendar.tz)		
							
			day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to,
																   calendar=contract.resource_calendar_id)
			
			for day, hours, leave in day_leave_intervals:				
				for lv in leave:
					holiday = lv.holiday_id					
					if holiday.holiday_status_id.name != 'Sick Time Off':
						_logger.log(25,'2222222222222222222')
						_logger.log(25,holiday.holiday_status_id.name)
						current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
							'work_entry_type_id': self.env.ref('l10n_qa_hr_payroll.work_entry_type_global'),
							'number_of_days': 0.0,
							'number_of_hours': 0.0,
						})
						current_leave_struct['number_of_hours'] += hours
						work_hours = calendar.get_work_hours_count(
							tz.localize(datetime.combine(day, time.min)),
							tz.localize(datetime.combine(day, time.max)),
							compute_leaves=False,
						)						
						if work_hours:
							current_leave_struct['number_of_days'] += hours / work_hours
					if holiday.holiday_status_id.name == 'Sick Time Off':						
						current_leave_struct_sick = leaves.setdefault(holiday.holiday_status_id, {
							'work_entry_type_id': self.env.ref('l10n_qa_hr_payroll.work_entry_type_sick_timeoff'),
							'number_of_days': 0.0,
							'number_of_hours': 0.0,
						})
						current_leave_struct_sick['number_of_hours'] += hours
						work_hours = calendar.get_work_hours_count(
							tz.localize(datetime.combine(day, time.min)),
							tz.localize(datetime.combine(day, time.max)),
							compute_leaves=False,
						)
						if work_hours:
							current_leave_struct_sick['number_of_days'] += hours / work_hours
						# for line in self.worked_days_line_ids:				
							# 	if line.name == 'Attendance':
							# 		# raise UserError(str("a_days"))
							# 		a_days += line.number_of_days
							# 		a_hours += line.number_of_hours
										# res.append(current_leave_struct_sick)	

			# res.extend(leaves.values())


		#     # compute sick leave days
			yth_sick_leaves = 0
			ytd_sick_leaves = 0
			hours_paid_sick_leave_6 = 0
			hours_paid_sick_leave_24 = 0

			paid_sick_leave_struct = {
				'work_entry_type_id': self.env.ref('l10n_qa_hr_payroll.work_entry_type_sick_timeoff'),
				'sequence': 6,
				'name': 'Paid Sick Leave',
				'code': 'PaidSickLeave',
				'number_of_days': 0.0,
				'number_of_hours': 0.0,
				'contract_id': contract.id,
			}
			partially_paid_sick_leave_struct = {
				'work_entry_type_id' : self.env.ref('l10n_qa_hr_payroll.work_entry_type_partially'),
				'name': 'Partially_Paid_Sick_Leave',
				'sequence': 7,
				'code': 'PartiallyPaidSickLeave',
				'number_of_days': 0.0,
				'number_of_hours': 0.0,
				'contract_id': contract.id,
			}
			unpaid_sick_leave_struct = {
				'work_entry_type_id' : self.env.ref('l10n_qa_hr_payroll.work_entry_type_unpaid'),
				'name': 'Unpaid_Sick_Leave',
				'sequence': 8,
				'code': 'UnpaidSickLeave',
				'number_of_days': 0.0,
				'number_of_hours': 0.0,
				'contract_id': contract.id,
			}

			d = datetime.strptime(str(self.date_to), '%Y-%m-%d')
			first_day = datetime.strptime(str(date(d.year, 1, 1)), '%Y-%m-%d')
			first_day_leave_intervals = contract.employee_id.list_leaves(first_day, day_to,
																		 calendar=contract.resource_calendar_id)

			
			for day, hours, leave in first_day_leave_intervals:
				for l in leave:
					holiday = l.holiday_id					
					if holiday.holiday_status_id.name == 'Sick Time Off':
						yth_sick_leaves += hours
						sick_work_hours = calendar.get_work_hours_count(
							tz.localize(datetime.combine(day, time.min)),
							tz.localize(datetime.combine(day, time.max)),
							compute_leaves=False,
						)						

						if sick_work_hours:
							ytd_sick_leaves += hours / sick_work_hours


							for values in leaves:								
								if values['name'] == 'Sick Time Off':
									if ytd_sick_leaves <= 14:																	
										paid_sick_leave_struct['number_of_days'] = current_leave_struct_sick[
											'number_of_days']
										paid_sick_leave_struct['number_of_hours'] = current_leave_struct_sick[
											'number_of_hours']
										hours_paid_sick_leave_6 = yth_sick_leaves


									elif ytd_sick_leaves <= 28:

										if (ytd_sick_leaves - current_leave_struct_sick['number_of_days']) <= 14:
											_logger.info("entered if of 24")

											paid_sick_leave_struct['number_of_days'] = 14 - ytd_sick_leaves + \
																					   current_leave_struct_sick[
																						   'number_of_days']
											paid_sick_leave_struct["number_of_hours"] = current_leave_struct_sick[
																							'number_of_hours'] - (
																									yth_sick_leaves - hours_paid_sick_leave_6)

											partially_paid_sick_leave_struct['number_of_days'] = ytd_sick_leaves - 14
											partially_paid_sick_leave_struct[
												'number_of_hours'] = yth_sick_leaves - hours_paid_sick_leave_6
										else:

											partially_paid_sick_leave_struct['number_of_days'] = current_leave_struct_sick[
												'number_of_days']
											partially_paid_sick_leave_struct['number_of_hours'] = current_leave_struct_sick[
												'number_of_hours']
											hours_paid_sick_leave_24 = yth_sick_leaves
											

									else:
										if (ytd_sick_leaves - current_leave_struct_sick['number_of_days']) <= 14:
											
											paid_sick_leave_struct['number_of_days'] = 6 - ytd_sick_leaves + \
																					   current_leave_struct_sick[
																						   'number_of_days']
											paid_sick_leave_struct["number_of_hours"] = current_leave_struct_sick[
																							'number_of_hours'] - (
																									yth_sick_leaves - hours_paid_sick_leave_6)

											partially_paid_sick_leave_struct['number_of_days'] = ytd_sick_leaves - 14
											partially_paid_sick_leave_struct[
												'number_of_hours'] = yth_sick_leaves - hours_paid_sick_leave_6

											
										elif (ytd_sick_leaves - current_leave_struct_sick['number_of_days']) <= 28:
											
											partially_paid_sick_leave_struct['number_of_days'] = 28 - ytd_sick_leaves + \
																								 current_leave_struct_sick[
																									 'number_of_days']
											partially_paid_sick_leave_struct['number_of_hours'] = current_leave_struct_sick[
																									  'number_of_hours'] - (
																											  yth_sick_leaves - hours_paid_sick_leave_24)

											unpaid_sick_leave_struct['number_of_days'] = ytd_sick_leaves - 28
											unpaid_sick_leave_struct[
												'number_of_hours'] = yth_sick_leaves - hours_paid_sick_leave_24

											
										else:
											_logger.info("entered else of else")
											_logger.info(ytd_sick_leaves - current_leave_struct_sick['number_of_days'])

											unpaid_sick_leave_struct['number_of_days'] = current_leave_struct_sick[
												'number_of_days']
											unpaid_sick_leave_struct['number_of_hours'] = current_leave_struct_sick[
												'number_of_hours']

											
			if paid_sick_leave_struct['number_of_days'] != 0:
				res.append(paid_sick_leave_struct)
			if partially_paid_sick_leave_struct['number_of_days'] != 0:
				# raise UserError(str(partially_paid_sick_leave_struct))
				res.append(partially_paid_sick_leave_struct)
			if unpaid_sick_leave_struct['number_of_days'] != 0:
				res.append(unpaid_sick_leave_struct)
			# if current_leave_struct['number_of_days'] != 0:
			# 	res.append(current_leave_struct)
			# if current_leave_struct_sick['number_of_days'] != 0:
			# 	res.append(current_leave_struct_sick)		

			# compute worked days
			work_data = contract.employee_id._get_work_days_data(day_from, day_to,compute_leaves=False,calendar=contract.resource_calendar_id)
			# raise UserError(work_data)
			# work_days100 = 0
			# work_hours100 = 0
			# u_days = 0
			# u_hours = 0
			# a_days = 0
			# a_hours = 0
			# for line in self.worked_days_line_ids:				
			# 	if line.name == 'Attendance':
			# 		# raise UserError(str("a_days"))
			# 		a_days += line.number_of_days
			# 		a_hours += line.number_of_hours
			# 	if line.name == 'Unemployment':
			# 		# raise UserError(str("a_days"))
			# 		u_days += line.number_of_days
			# 		u_hours += line.number_of_hours
			# if a_days > 0:		
			# 	work_days100 += a_days - u_days
			# 	work_hours100 += a_hours- u_hours		
			attendances = {
				'work_entry_type_id': self.env.ref('l10n_qa_hr_payroll.work_entry_type_normal_working_days_100'),
				# 'name': _("Normal Working Days paid at 100%"),
				# 'sequence': 1,
				# 'code': 'WORK100',
				'number_of_days': work_data['days'],#work_days100,
				'number_of_hours': work_data['hours'],#work_hours100,
				# 'contract_id': contract.id,
			}
			res.append(attendances)

			# compute the total working day of that particular month
			# working_data = contract.employee_id._get_work_days_data(day_from, day_to,compute_leaves=False,
			# 														  calendar=contract.resource_calendar_id)
			# working_days = {
			# 	'work_entry_type_id': self.env.ref('l10n_qa_hr_payroll.work_entry_type_normal_working_days'),
			# 	# 'sequence': 1,
			# 	# 'code': 'WORKDAYS',
			# 	'number_of_days': working_data['days'],
			# 	'number_of_hours': working_data['hours'],
			# 	# 'contract_id': contract.id,
			# }
			# 			# res.append(attendances)
			# res.append(working_days)
			# _logger.log(25,'jjjjjjjjjjjjjjjjjjjjj')
			# _logger.log(25,res)
		# return res


			# for work_entry_type_id, hours in work_hours_ordered:
			# 	# raise UserError(str(""))
			# 	work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
			# 	is_paid = work_entry_type_id not in unpaid_work_entry_types
			# 	calendar = contract.resource_calendar_id
			# 	days = round(hours / calendar.hours_per_day, 5) if calendar.hours_per_day else 0
			# 	if work_entry_type_id == biggest_work:
			# 		days += add_days_rounding
			# 	day_rounded = self._round_days(work_entry_type, days)
			# 	add_days_rounding += (days - day_rounded)
			# 	attendance_line = {
			# 		'sequence': work_entry_type.sequence,
			# 		'work_entry_type_id': work_entry_type_id,
			# 		'number_of_days': day_rounded,
			# 		'number_of_hours': hours,
			# 		'amount': hours * paid_amount / total_hours if is_paid else 0,
			# 	}
			# 	# raise UserError(str(total_hours))
			# 	res.append(attendance_line)
		return res

# class HrPayrollStructure(models.Model):
# 	_inherit = 'hr.payroll.structure'
# 	_description = 'Salary Structure'

# 	@api.model
# 	def _get_default_rule_ids(self):
# 		raise UserError(str(""))
# 		di = {
# 				'name': 'Basic Salary',
# 				'sequence': 325,
# 				'code': 'UNEMPLOYMENT',
# 				'category_id': self.env.ref('hr_payroll.DED').id,
# 				'condition_select': 'worked_days.Unemployment and worked_days.Unemployment.number_of_days or False',
# 				'amount_select': 'code',
# 				'amount_python_compute': 'result = (BASIC + categories.ALW)*(worked_days.Unemployment.number_of_days or 0)/worked_days.WORKDAYS.number_of_days',
# 			}
# 		res = super(HrPayrollStructure, self)._get_default_rule_ids()
# 		raise UserError(str(res))
