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
from datetime import datetime
from dateutil import relativedelta as rdelta
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning


########### For Expense Contract Details ###########
class expense_contract(models.Model):
    """" For Expense Contract Details"""
    _name = 'expense.contract'
    
    @api.one
    @api.depends('start_date', 'end_date')
    def _get_period(self):
        self.period = 0
        if self.start_date and self.end_date:
            rd = rdelta.relativedelta(datetime.strptime(self.end_date, '%Y-%m-%d'), datetime.strptime(self.start_date, '%Y-%m-%d'))
            self.period = rd.months + 1

    @api.one
    @api.depends('per_home_expenses','soc_electricity_bill','guard_salary','soc_maintenance')
    def _get_total_amount(self):
        self.total = 0.0
        if self.soc_electricity_bill and self.guard_salary and self.soc_maintenance:
            self.total = self.soc_electricity_bill + self.guard_salary + self.soc_maintenance 

    @api.one
    @api.depends('total','no_house')
    def _get_total_per_house(self):
        self.total_per_house = 0.0
        if self.total and self.no_house and self.no_house != 0:
            res_total = str(self.total/self.no_house)
            total_list = res_total.split('.')
            res_tot = float(total_list[1])
            if float(total_list[1]) > 0.0 :
                total =  float(total_list[0])+1.0
            else:
                total = float(total_list[0])
            self.total_per_house = total
        
    @api.one
    @api.depends('no_house','expense_line_ids')
    def _get_remain_invoice(self):
        if self.no_house:
            self.remain_inv_paid = self.no_house - len(self.expense_line_ids)
#            if self.no_house != self.remain_inv_paid:
#                self.is_remain_inv = True
        else:
            self.remain_inv_paid = 0
    
    @api.one
    @api.depends('total','expense_line_ids')
    def _get_amount(self):
        self.total_remain_amount = 0.0
        self.total_collect_amount = 0.0
        if self.total and self.expense_line_ids:
            total_res = 0.0
            for line in self.expense_line_ids:
                total_res += line.total
            self.total_collect_amount = total_res
            self.total_remain_amount = self.total_collect_amount - self.total

    number = fields.Char('Number')
    society_division_id = fields.Many2one('society.division','Select Society Division',required=True,help='Name of Division/Block.')
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    period = fields.Integer(compute='_get_period', string='Period', help="1-12")
    no_house = fields.Integer('Total House', readonly=True, help='No of houses.')
    remain_inv_paid = fields.Integer(compute='_get_remain_invoice',string='Remain Invoices', readonly=True)
#    is_remain_inv = fields.Boolean('Is Remain Invoices', default=False)
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('gen_invoices','Generated Invoices'),('done','Done')], 'Status', default="draft")
    soc_electricity_bill = fields.Float('Electricity Bill',required=True,help='Total electricity bill of use in society [Ex.use street-Lite/Lift/water supply].')
    per_home_expenses = fields.Float('Add Funds',required=True,help='Use in society funds.')
    guard_salary = fields.Float('Security Guards Salary',required=True,help='Security guard salary of month.')
    soc_maintenance = fields.Float('Other Expenses',required=True,help='Other society maintenance charges [Ex.Road clean/Garden/].')
    expense_line_ids = fields.One2many('society.expense.line','contract_id','Invoice Line')
    total = fields.Float(compute='_get_total_amount',string='Total Amount')
    total_per_house = fields.Float(compute='_get_total_per_house',string='Total Per House')
    total_collect_amount = fields.Float(compute='_get_amount',string='Total Collect')
    total_remain_amount = fields.Float(compute='_get_amount',string='Total Remain')
    notes = fields.Text('Description')
    is_saved = fields.Boolean('Is Saved?')

    @api.onchange('start_date','end_date')
    def onchange_date(self):
        warning = {}
        result = {}
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                warning = {
                    'title': _('Warning!'),
                    'message': _("End date must be greater than start date.")
                }
                result['warning'] = warning
                self.end_date = False
        return result


    @api.model
    def create(self, vals):
        prev_exp_rec = self.search([('state','!=','done')])
        if prev_exp_rec:
            raise except_orm(_('Error!'), _("You can not create because previous invoice expense not done!"))
        if vals.get('society_division_id'):
            house_ids = self.env['home.details'].search([('society_division_id', '=', vals.get('society_division_id'))])
            no_house_length = len(house_ids.ids)
            vals.update({'no_house' : no_house_length, 'is_saved': True})
        return super(expense_contract, self).create(vals)
    
    @api.multi
    def write(self, vals):
        if vals.get('society_division_id'):
            house_ids = self.env['home.details'].search([('society_division_id', '=', vals.get('society_division_id'))])
            no_house_length = len(house_ids.ids)
            vals.update({'no_house' : no_house_length})
        return super(expense_contract, self).write(vals)
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'done' or rec.expense_line_ids:
                raise except_orm(_('Error!'), _("You can not delete done expense order!"))
#                raise except_orm(_('Error!'), _("You can not delete done expense order! If you want to delete order first delete related Invoices."))
        return super(expense_contract, self).unlink()
    
    @api.multi
    def onchange_society_division(self,society_division_id, context):
        house_ids = self.env['home.details'].search([('society_division_id', '=', society_division_id)])
        no_house_length = len(house_ids.ids)
        res = {'value': {'no_house':no_house_length}}
        return res
    
    @api.multi
    def action_confirm(self):
        soc_exp_rec = self.browse(self.ids)
        date_start = soc_exp_rec.start_date
        date_end = soc_exp_rec.end_date
        sq_start_date = datetime.strptime(date_start,'%Y-%m-%d').strftime('%d/%m')
        sq_end_date = datetime.strptime(date_end,'%Y-%m-%d').strftime('%d/%m/%Y')
        sq_no = str(self.society_division_id.name+'-'+sq_start_date+'-'+sq_end_date)
        if self.no_house != 0 :
            self.write({'state':'confirm','number':sq_no})
        else:
            raise Warning (_("Please select must be one Society Division in one house!"))
    @api.multi
    def action_generate_invoice(self):
        soc_exp_rec = self.browse(self.ids)
        sq_no = soc_exp_rec.number
        inv_details_obj = self.env['account.invoice']
        home_details_obj = self.env['home.details']
        home_details_ids = home_details_obj.search([('society_division_id','=',self.society_division_id.id)])
        for home_details_rec in home_details_ids: 
            vals = {
                    'seq_no': self.number,
                    'home_id': home_details_rec.id,
                    'owner_id': home_details_rec.owner_id.id,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'soc_electricity_bill': self.soc_electricity_bill,
                    'guard_salary': self.guard_salary,
                    'soc_maintenance': self.soc_maintenance,
                    'per_home_expenses': self.per_home_expenses,
                    'pre_credit_amount': home_details_rec.pre_credit_amount,
                    'pre_debit_amount': home_details_rec.pre_debit_amount,
                    'total_expense': self.total_per_house,
                    'total': (self.total_per_house + self.per_home_expenses),
                    'total_expense_amount': 0.0,
                    'state':'unpaid'
                    }
            inv_details_obj.create(vals)
        self.write({'state':'gen_invoices'})
    
    @api.multi
    def action_done(self):
        if not self.expense_line_ids and self.no_house != 0:
            raise Warning(_("Please check remain invoices!"))
        if self.expense_line_ids:
            if self.no_house == len(self.expense_line_ids.ids) and self.remain_inv_paid == 0:
                soc_funds_obj = self.env['society.funds']
                soc_funds_line_obj = self.env['society.funds.line']
                soc_funds_ids = soc_funds_obj.search([])
                if not soc_funds_ids:
                    soc_funds_ids = soc_funds_obj.create({'seq_no':self.number,
                                                          'date': time.strftime("%Y-%m-%d"),
                                                          'total':0.0})
                print '===dfdf', soc_funds_ids
                soc_funds_line_obj.create({'seq_no':self.number,
                                           'date': time.strftime("%Y-%m-%d"),
                                           'total':(self.per_home_expenses * self.no_house),
                                           'soc_funds_id':soc_funds_ids.id})
#                self.write({'state':'done'})
            else:
                raise Warning(_("Please check remain invoices !"))


########### For Expense Line Details ###########
class society_expense_line(models.Model):
    """"For Society Expense Line Details"""
    _name = 'society.expense.line'
    _rec_name = 'home_no'
    
    contract_id = fields.Many2one('expense.contract','Invoices')
    home_id = fields.Many2one('home.details','Home Id')
    home_no = fields.Char('Home No', related='home_id.home_no')
    owner_id = fields.Many2one('res.partner','Owner Name')
    payment_date = fields.Date('Payment Date')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    total = fields.Float('Total')
#    water_expense = fields.Float('Total Water Expense', readonly=True)
    total_expense_amount = fields.Float('Total Expense Amount')
    paid_amount = fields.Float('Paid Amount')
    credit = fields.Float('Credit Amount')
    debit = fields.Float('Debit Amount')

