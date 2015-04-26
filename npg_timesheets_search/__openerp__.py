# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group INC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
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
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': 'Project Search Timesheet Lines',
    'version': '1.0',
    'category': '',
    "sequence": 14,
    'complexity': "easy",
    'category': 'Project',
    'description': """
    Adds  new search wizard in Time tracking to allow to search time entries by  Users and Date ranges
    Adds feature to recreate any deleted time sheet lines that were created from project task work lines
            
    """,
    'author': 'NovaPoint Group Inc, Stephen Levenhagen',
    'website': 'www.novapointgroup.com',
    'depends': ['project_timesheet',],
    'init_xml': [],
    'data': ["wizard/hr_timesheet_working_hours_wizard.xml",
             "views/search_view.xml",
             "views/menu_view.xml",
             ],
    'demo_xml': [],
    'test': [],
    'qweb' : [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
