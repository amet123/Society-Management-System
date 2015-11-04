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
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

########### Use For Generate Meter Number ###########
class generate_meter_number(models.TransientModel):
    """" For Generate Meter Number"""
    _name = 'generate.meter.number'


    @api.model
    def default_get(self, fields):
        context = self._context
        if context is None:
            context = {}
        res = super(generate_meter_number, self).default_get(fields)
        if 'owner_id' in fields:
            res.update({'owner_id': context.get('default_owner_id')})
        if 'home_id' in fields:
            res.update({'home_id': context.get('default_home_id')})
        if 'society_division_id' in fields:
            res.update({'society_division_id': context.get('default_soc_division_id')})
        if 'is_active' in fields:
            res.update({'is_active': context.get('default_new_meter')})
        if 'is_replace_meter' in fields:
            res.update({'is_replace_meter': context.get('default_replace_meter')})
        return res

    meter_no = fields.Char('Meter No')
    home_id = fields.Many2one('home.details','Home Id')
    owner_id = fields.Many2one('res.partner',string='Owner Name')
    society_division_id = fields.Many2one('society.division',string='Society Division')
    conn_date = fields.Date('ConnectionDate', help='[Meter Connection Date]')
    conn_fees = fields.Float('Connection Fees')
    replace_charge = fields.Float('Replace Meter Charge')
    is_active = fields.Boolean('Is Active')
    de_active = fields.Boolean('De Active')
    replace_meter_date = fields.Date('Replace Date')
    is_replace_meter = fields.Boolean('Replace Meter')
    reason = fields.Char('Reason')
    note = fields.Text('Note', help='Add Additional Information.')

    @api.multi
    def action_new_number(self):
        meter_obj = self.env['meter.meter']
        home_details_obj = self.env['home.details']
        home_ids = home_details_obj.search([('id', '=', self._context.get('active_ids'))])
        for rec in self:
            meter_ids = meter_obj.search([('meter_no','=', rec.meter_no)])
            if meter_ids:
                raise Warning(_("Please Enter Unique Meter Number"))
            if not meter_ids:
                if not home_ids.meter_id:
                    new_meter_vals = {
                            'meter_no': rec.meter_no,
                            'home_id': rec.home_id.id,
                            'owner_id': rec.owner_id.id,
                            'society_division_id': rec.society_division_id.id,
                            'conn_date': rec.conn_date,
                            'conn_fees': rec.conn_fees,
                            'is_active': True,
                            'note': rec.note,
                            'state': 'active',
                            }
                    new_meter_id = meter_obj.create(new_meter_vals)
                    home_ids.write({'meter_id':new_meter_id.id, 'is_active_meter':True})
                if home_ids.meter_id and self._context.get('is_replace_meter'):
                    home_ids.meter_id.write({'is_active': False,
                                             'replace_meter':True,
                                             'reason':rec.reason,
                                             'new_meter_no':rec.meter_no,
                                             'replace_meter_date': rec.replace_meter_date,
                                             'replace_charge': rec.replace_charge,
                                             'state': 'closed'})
                    replace_meter_vals = {
                            'meter_no': rec.meter_no,
                            'home_id': rec.home_id.id,
                            'owner_id': rec.owner_id.id,
                            'society_division_id': rec.society_division_id.id,
                            'conn_date': rec.replace_meter_date,
                            'conn_fees': rec.replace_charge,
                            'is_active': True,
                            'note': rec.note,
                            'state': 'active',
                            }
                    replace_meter_id = meter_obj.create(replace_meter_vals)
                    home_ids.write({'meter_id':replace_meter_id.id, 
                                    'is_replace_meter':True})

