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


########### For Society Complaints ###########
class society_complaints(models.Model):
    """For Society Complaints Details"""
    _name = 'society.complaints'
    _rec_name = 'complaints_no'
    
    complaints_no = fields.Char('Complaints No')
    title = fields.Char('Title', required=True)
    complainer_name = fields.Char('Complainer Name', required=True)
    home_id = fields.Many2one('home.details','Home Id', required=True)
    owner_id = fields.Char(string='Owner Name',related="home_id.owner_id.name")
    date_complaints = fields.Date('Date', default=lambda *a: time.strftime('%Y-%m-%d'), required=True, help="Date of complaints.")
    day_problem = fields.Integer('Days of Problem', help='How many days to problem fetch you.')
    problem_reason = fields.Char('Reason', help="You know about problem reason.")
    state = fields.Selection([('draft','Draft'),('progress','Progress'),('done','Done')], string="Status", default='draft')
    review = fields.Selection([('0','0'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], string='Review', help='Review by complainer.')
    note = fields.Text('Review', help='Enter additional information of complaints.')
    prob_process_days = fields.Char('Problem Solve Days', help='How many days for solve problem.')
#    user_satisfy = fields.Boolean('Use Satisfied', help='User is satisfied or not.')
    
    @api.model
    def create(self, vals):
        prev_rec = self.search([])
        date = time.strftime('%Y-%m-%d')
        mon_year_res = datetime.datetime.strptime(date, '%Y-%m-%d').strftime("%b-%Y")
        if not prev_rec:
            next_res = '0001'
            vals.update({'complaints_no' : mon_year_res+ ' - ' + next_res})
        if prev_rec:
            complaints_ids = prev_rec.ids
            length = len(complaints_ids)
            res = ''
            if length <= 8:
                next_no = '000'+str(length+1)
                res = mon_year_res+ ' - ' + next_no
            if length <= 98 and length >= 9:
                next_no = '00'+str(length+1)
                res = mon_year_res+ ' - ' + next_no
            if length <= 998 and length >= 99:
                next_no = '0'+str(length+1)
                res = mon_year_res+ ' - ' + next_no
            vals.update({'complaints_no' : res})
        return super(society_complaints, self).create(vals)
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise except_orm(_('Error!'), _("You can not delete Done Expense Order!"))
        return super(society_complaints, self).unlink()
