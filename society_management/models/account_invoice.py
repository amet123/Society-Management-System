# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author by Pankaj Goyani (goyanipankaj13@gmail.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
##############################################################################

import time
import datetime
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning


########### For Account Invoice Details ###########
class account_invoice(models.Model):
    """For Society Houses Invoice Details"""
    _inherit = 'account.invoice'

    @api.one
    @api.depends('prev_meter_reading','curr_meter_reading','per_unit_charge')
    def _get_reading_total(self):
        self.total_use_reading = 0.0
        self.total_charge = 0.0
        if self.curr_meter_reading:
            self.total_use_reading = self.curr_meter_reading - self.prev_meter_reading
            self.total_charge = self.total_use_reading * self.per_unit_charge
    
    @api.one
    @api.depends('is_use_water_meter','total_charge','per_home_expenses','total_expense','pre_credit_amount','pre_debit_amount',)
    def _get_total(self):
        self.total = self.total_charge + self.per_home_expenses + self.total_expense
        self.total_expense_amount = self.total
        if self.pre_credit_amount:
            
            self.total_expense_amount = self.total - self.pre_credit_amount
        if self.pre_debit_amount:
            self.total_expense_amount = self.total - self.pre_debit_amount

    @api.one
    @api.depends('total_expense_amount','paid_amount')
    def _get_credit_debit(self):
        self.credit = 0.0
        self.debit = 0.0
        if self.total_expense_amount and self.paid_amount:
            total = (self.paid_amount - self.total_expense_amount)
            if total > 0:
                self.credit = total
            if total < 0:
                self.debit = total
#
    seq_no = fields.Char('Number')
    home_id = fields.Many2one('home.details','Home Id')
    owner_id = fields.Many2one('res.partner','Owner Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    payment_date = fields.Date('Payment Date')
    state = fields.Selection([('unpaid','unpaid'),('paid','Paid')], 'Status', default="unpaid")
    soc_electricity_bill = fields.Float('Electricity Bill',help='Total electricity bill of use in society [Ex.use Street-lite/Lift/Water-supply].')
    per_home_expenses = fields.Float('Add Funds', help='Use in society funds')
    # Use Water Meter For Supply Water.
    is_use_water_meter = fields.Boolean('Use Water Meter?', help='Use water meter.')
    meter_id = fields.Many2one('meter.meter',string='Meter Id')
    meter_no = fields.Char(string='Meter No')
    prev_meter_reading = fields.Float('Previous Reading', help='Previous Meter reading Unit.')
    prev_meter_reading_date = fields.Date('Previous Reading Date', help='Previous Meter reading Date.')
    curr_meter_reading = fields.Float('Meter Reading', help='Current meter Reading Unit.')
    curr_reading_date = fields.Date('Reading Date', help='Date of Meter reading.')
    per_unit_charge = fields.Float('Per Unit Charge', help='Per unit charge.')
    total_use_reading = fields.Float(compute='_get_reading_total',string='Total Consumption',store=True)
    total_charge = fields.Float(compute='_get_reading_total',string='Total Charge', store=True)
    is_remain_reading = fields.Boolean('Generate Reading?', default=True)
    
    guard_salary = fields.Float('Security Guards Salary')
    soc_maintenance = fields.Float('Other Expenses', help='[Other maintenance charges [Ex.Road-cleaning/Garden/].')
    total = fields.Float(compute='_get_total', string='Total')
    total_expense = fields.Float('Total Expense')
    total_expense_amount = fields.Float(compute='_get_total', store=True, string='Total Expense Amount')
    paid_amount = fields.Float('Paid Amount')
    pre_credit_amount = fields.Float('Previous Credit Amount')
    pre_debit_amount = fields.Float('Previous Debit Amount')
    credit = fields.Float(compute='_get_credit_debit', store=True, string='Credit')
    debit = fields.Float(compute='_get_credit_debit', store=True, string='Debit')
    
    @api.multi
    def action_paid_invoice(self):
        if self.paid_amount == 0.0 and self.total_expense_amount >= 0.0:
            raise Warning(_("Please Enter Paid Amount!"))
        else:
            #For create society expense lines of (invoice lines)
            exp_contract_obj = self.env['expense.contract']
            contract_ids = soc_contract_obj.search([('number','=',self.seq_no),
                                ('start_date','=',self.start_date),('end_date','=',self.end_date)])
            soc_exp_line_obj = self.env['society.expense.line']
            vals_exp_line = {
                    'contract_id': contract_ids.id,
                    'home_id': self.home_id.id,
                    'owner_id': self.owner_id.id,
                    'payment_date': self.payment_date,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'total_expense_amount': self.total_expense_amount,
                    'total':self.total,
                    'paid_amount': self.paid_amount,
                    'credit': self.credit,
                    'debit': self.debit,
                    }
            soc_exp_line_obj.create(vals_exp_line)
            
            if self.is_use_water_meter:
                #For create water meter details in Home 
                vals_water_meter = {
                        'home_id': self.home_id.id,
                        'prev_reading_unit': self.prev_meter_reading,
                        'prev_reading_date': self.prev_meter_reading_date,
                        'curr_reading_unit': self.curr_meter_reading,
                        'curr_reading_date': self.curr_reading_date,
                        'per_unit_charge': self.per_unit_charge,
                        'total_use_reading': self.total_use_reading,
                        'total': self.total_charge,
                        }
                self.env['water.meter'].create(vals_water_meter)
            
            self.home_id.write({'bill_sqn_no': self.seq_no,
                                'payment_date': self.payment_date,
                                'pre_credit_amount': self.credit,
                                'pre_debit_amount': self.debit})
            self.write({'state':'paid'})
    
    @api.multi
    def action_meter_reading(self):
        self.is_remain_reading = False
        # Meter configuration search for this duration of invoice
        water_meter_config_obj = self.env['water.meter.config']
        meter_config_ids = water_meter_config_obj.search([('date_start', '<=', self.start_date),
                                                          ('date_stop', '>=', time.strftime('%Y-%m-%d')),
                                                          ('is_active','=',True)])
        if meter_config_ids:
            per_unit_charge_res = meter_config_ids[0].per_unit_charge
            home_details_obj = self.env['home.details']
            self.curr_meter_reading = 0.0
            self.per_unit_charge = per_unit_charge_res
            # for Home details in water meter details
            water_meter_ids = self.home_id.water_meter_ids
            if water_meter_ids:
                # IF meter reading is available in home details...
                self.write({'prev_meter_reading_date': water_meter_ids[-1].curr_reading_date,
                            'prev_meter_reading':water_meter_ids[-1].curr_reading_unit,
                            'curr_reading_date': time.strftime('%Y-%m-%d'),
                            'meter_id':self.home_id.meter_id.id
                            })
            #IF no meter line for that meter means first time note a reading...
            else:
                self.write({'prev_meter_reading_date': self.start_date,
                            'meter_id':self.home_id.meter_id.id,
                            'prev_meter_reading':0.0,
                            'curr_reading_date': time.strftime('%Y-%m-%d'),
                            })
        else:
                raise Warning(_("Please configure water meter reading per Unit Charge."))
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'paid':
                raise except_orm(_('Error!'), _("You can not delete paid Invoice!"))
        return super(account_invoice, self).unlink()
