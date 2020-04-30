# -*- coding: utf-8 -*-
{
    'name': "Qatar-Hr Payroll Management Localization",
    'summary': """Manage your employee payroll records""",
    'description': """
The module will add salary rule for salary components such as housing allowance, transportation allowance, telecom allowance,food allowance, sales commission allowance, 
special allowance, duty roaster allowance, income tax, pension plan and ticket to home country and also calculate the total payment and total company contribution for the employee payslip. 
Based on the language specified in the employee form, the module will generate payslip with dual language. It will also add the selected salary structure and the mode of payment in the contract report

The module will replace the existing odoo payslip with the following salary structure components:

                                        - Basic Salary
                                        - Housing Allowance
                                        - Transportation Allowance
                                        - Telecom Allowance
                                        - Food Allowance
                                        - Duty Roaster Allowance
                                        - Special Allowance
                                        - Encouragement Allowance
                                        - Sales Commission Allowance
                                        - Working Day Overtime
                                        - Holiday Duty Overtime
                                        - Basic Salary Adjustment
                                        - Housing Allowance Adjustment
                                        - Transportation Allowance Adjustment
                                        - Telecom Allowance Adjustment
                                        - Special Allowance Adjustment
                                        - Annual Bonus
                                        - Annual Ticket
                                        - Income Tax
                                        - Advance Salary Recovery
                                        - Unpaid Leave Deduction
                                        - Pilgrimage Leave Deduction
                                        - Partially Paid Sick Leave Deduction
                                        - Unpaid Sick Leave Deduction
                                        - Unemployment Deduction
                                        - Pension Plan Deduction
                                        - Other Deductions
                                        - Total Payment
                                        - Pension Plan
                                        - Total Company Contribution
""",
    'author': "Zmakan Technical Solution",
    'website': "http://www.zmakan.com",
    'category': 'Human Resources',
    'version': '12.0.4',
    'depends': ['base','hr','resource','hr_contract','hr_payroll'],
    'data': [
        'data/data.xml',
        'data/l10n_qa_hr_payroll_data.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_employee_relation.xml',
        'views/hr_employee_religion.xml',
        'views/l10n_qa_hr_payslip.xml',
        # 'views/report_contract_template_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}