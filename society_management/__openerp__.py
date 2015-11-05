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

{
    'name': 'Society Management System',
    'version': '0.02',
    'author': 'Pankaj Goyani',
    'category': 'Expense',
    'website': ['goyanoipankaj13@gmail.com'],
    'sequence': 1,
    'depends': ['report', 'account'],
    'description': """
Society Management.
====================================

Provide Management:
--------------------------------------------
    * Home Details
    * Divisions

    * General Accounting:
    * Expenses
    * Invoices
    * Funds Management

    * Events

    * Society Complaints
    * Society Funds

    * Meter Details

Creates a dashboard for accountants that includes:
--------------------------------------------------
    * List of Homes to Remain Amounts
    * Analysis of Water Meters


    This module helps to manage your Residential and Commercial & Housing Societies.
    Say goodbye to procedures of maintain your society files and documents in paper.
    """,
    'data': [
            'data/product_data.xml',
            'wizard/create_meter.xml',
            'views/society_details_view.xml',
            'views/expense_contract_view.xml',
            'views/account_invoice_view.xml',
            'views/complaints_view.xml',
            'views/society_config_view.xml',
            'views/society_report.xml',
            'views/report_home_invoice.xml',
            ],
    'demo': ['demo/society_demo.xml'],
    'auto_install': False,
    'installable': True,
    'application': False
}
