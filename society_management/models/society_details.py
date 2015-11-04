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


########### For Divisions Details ###########
class society_division(models.Model):
    """"For Society Division"""
    _name="society.division"

    @api.one
    @api.depends('is_configured', 'home_details_ids')
    def _get_total_house(self):
        total = 0
        home_from = home_to = ''
        if self.home_details_ids and self.is_configured:
            home_from = self.home_details_ids[0].home_no
            home_to = self.home_details_ids[-1].home_no
            total = len(self.home_details_ids)
        self.home_from = home_from
        self.home_to = home_to
        self.no_of_house = total

    @api.one
    @api.depends('is_lift')
    def _get_lift(self):
        self.lift = 'No'
        if self.is_lift:
            self.lift = 'Yes'

    name = fields.Char('Name', help="For name of society division [Ex.A,B,C...]")
    image = fields.Binary(string='Image')
    house_area = fields.Char('House Area', help='House Area [Ex. 150 sq ft, 250 sq ft.]')
    house_bhk = fields.Char('House BHK', help="House BHK [Ex, 2BHK, 3BHK, 3.5BHK, 4BHK.]")
    home_from = fields.Char(compute='_get_total_house', string='From')
    home_to = fields.Char(compute='_get_total_house', string='To')
    no_of_house = fields.Integer(compute='_get_total_house',string='Total House', help='Total number of house in this Section or Block.')
    floor = fields.Integer('Floor', help='How many floor.')
    is_lift = fields.Boolean('Lift', help='This Division have a lift facility or not.')
    lift = fields.Char(compute='_get_lift',string='Lift')
    home_details_ids = fields.One2many('home.details','society_division_id', string='Home Details')
    is_configured = fields.Boolean('Complete Configure',help='All Homes Configured ?')
    color = fields.Integer('Color Index')


########### For Home Details ###########
class home_details(models.Model):
    """For Society House Details"""
    _name = 'home.details'
    _rec_name = 'home_no'

    @api.one
    @api.depends('vehicle_ids')
    def _get_vehicles_name(self):
        vehicles = 'No'
        if self.vehicle_ids:
            vehicles = ''
            counter = 0
            for veh_rec in self.vehicle_ids:
                if veh_rec.vehicle_type:
                    veh_type = veh_rec.vehicle_type
                    print '===', veh_type, type(veh_type)
                    if veh_type.find('_'):
                        veh_type = veh_type.replace('_', ' ',)
                    if counter == 1:
                        vehicles += veh_type +'/'
                    else:
                        vehicles += ' '+ veh_type +'/'
                    counter += 1
        self.vehicle_list = vehicles.title()


    home_no = fields.Char('Home No',required=True)
    image = fields.Binary(string='Image')
    owner_id = fields.Many2one('res.partner','Owner Name',required=True)
    contact_no = fields.Char('Mobile no',required=True)
    date = fields.Date('Date')
    no_persion = fields.Integer('No Persion',required=True)
    vehicle_ids = fields.One2many('vehicle.details','home_id', 'Vehicle Details')
    vehicle_list = fields.Char(compute='_get_vehicles_name',string='Vehicles')
    bill_sqn_no = fields.Char('Invoice Number')
    payment_date = fields.Date('Payment Date')
    pre_credit_amount = fields.Float('Previous Credit Amount')
    pre_debit_amount = fields.Float('Previous Debit Amount')
    society_division_id = fields.Many2one('society.division','Society Division', required=True, help='Name of division/Block of Society.')
    is_active_meter = fields.Boolean('Use Water Meter')
    is_replace_meter = fields.Boolean('Replace Meter')
    meter_id = fields.Many2one('meter.meter',string='Meter No')
    water_meter_ids = fields.One2many('water.meter','home_id', string='Water Meter')
    color = fields.Integer('Color Index')

    @api.multi
    def create_meter(self):
        if self._context is None:
            self._context = {}
        ctx = dict(
            default_owner_id=self.owner_id.id,
            default_home_id=self.id,
            default_soc_division_id=self.society_division_id.id,
        )
        if self.meter_id:
            ctx.update({'default_new_meter':True})
        if self.meter_id and self.is_replace_meter:
            ctx.update({'default_new_meter':True, 'default_replace_meter':True})
        return {
            'name': _('Create Meter Details'),
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'generate.meter.number',
            'view_id':False,
            'target': 'new',
            'context':ctx,
        }


########### For Society Vehicle Details ###########
class vehicle_details(models.Model):
    """For Society House Vehicle Details"""
    _name = 'vehicle.details'

    home_id = fields.Many2one('home.details','Home Id')
    vehicle_name = fields.Char('Vehicle Name')
    vehicle_type = fields.Selection([('car','Car'),('two_vehicle','Two Vehicle'),('bicycle','Bicycle')],string='Vehicle Type')
    vehicle_number = fields.Char('Vehicle Number')


########### For Society Funds ###########
class society_funds(models.Model):
    """For Society Funds(Credit or Debit) Details"""
    _name = 'society.funds'
    _rec_name = 'seq_no'
    
    seq_no = fields.Char('Seq No')
    date = fields.Date('Date', help='Date of collection funds.')
    prev_month_funds = fields.Float('Previous Month')
    total = fields.Float('Total')
    soc_funds_line_ids = fields.One2many('society.funds.line','soc_funds_id', string='Society Funds')


########### For Society Funds ###########
class society_funds(models.Model):
    """For Society Funds(Credit or Debit) Details"""
    _name = 'society.funds.line'
    _rec_name = 'seq_no'
    
    seq_no = fields.Char('Seq No')
    date = fields.Date('Date', help='Date of collection funds.')
    total = fields.Float('Total')
    soc_funds_id = fields.Many2one('society.funds','Funds Id')


