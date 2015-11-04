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


########### Use For Water Meter Configuration ###########
class meter_meter(models.Model):
    """For Society Home Water Meter"""
    _name = 'meter.meter'
    _rec_name = 'meter_no'
    
    meter_no = fields.Char('Meter No')
    home_id = fields.Many2one('home.details','Home Id')
    owner_id = fields.Many2one('res.partner',string='Owner Name',related='home_id.owner_id')
    society_division_id = fields.Many2one('society.division',string='Society Division',related='home_id.society_division_id')
    conn_date = fields.Date('Connection Date', help='Date Start.')
    conn_fees = fields.Float('Connection Fees')
    state = fields.Selection([('active', 'Active'),('closed', 'Closed')], state="Status")
    is_active = fields.Boolean('Is Active')
    
    replace_meter = fields.Boolean('Replace Meter')
    new_meter_no = fields.Char(string='New Meter Number')
    replace_meter_date = fields.Date('Replace Meter Date', help='Replace Meter Date.')
    replace_charge = fields.Float('Replace Meter Charge')
    reason = fields.Char('Reason')
    note = fields.Text('Note', help='Add Additional Information.')


########### For Water Meter Configuration ###########
class water_meter(models.Model):
    """For Society Home Water Meter Configuration Details"""
    _name = 'water.meter'
    
    home_id = fields.Many2one('home.details', 'Home Id')
    prev_reading_unit = fields.Float('Previous Reading Unit', help='Previous reading unit.')
    prev_reading_date = fields.Date('Previous Reading', help='Previous reading date.')
    curr_reading_unit = fields.Float('Current Reading Unit', help='Current reading unit.')
    curr_reading_date = fields.Date('Current Reading Date', help='Current reading date.')
    per_unit_charge = fields.Float('Per Unit Charge', help='Per unit charge.')
    total_use_reading = fields.Float('Total use reading', help='Total Consumption.')
    total = fields.Float('Total', help='Total.')


########### For Water Meter Configuration ###########
class water_meter_config(models.Model):
    """For Society Home Water Meter Configuration Details"""
    _name = 'water.meter.config'
    _rec_name = 'per_unit_charge'
    
    @api.constrains('date_start','date_stop')
    def _check_date(self):
        if self.date_start > self.date_stop:
            raise Warning(_('You can not enter End Date greater Start Date.'))
        
    date_start = fields.Date('Date Start')
    date_stop = fields.Date('Date Stop')
    is_active = fields.Boolean('Is Active', help="Use this Configuration")
    per_unit_charge = fields.Float('Per Unit Charge', help='Per Unit Charge.')
    note = fields.Text('Note', help='Add Additional Information.')

    @api.model
    def create(self, vals):
        warter_me_config_ids = self.search([('date_start','<=', vals.get('date_start')),
                                            ('date_stop','>=',vals.get('date_stop'))])
        if warter_me_config_ids:
            raise except_orm(_('Error!'), _("You can create Next Configuration after this date %s!"%(warter_me_config_ids[0].date_stop)))
        return super(water_meter_config, self).create(vals)