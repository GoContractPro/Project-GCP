# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 NovaPointGroup LLC.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'NPG Project Enhancements',
    'version': '1.0',
    'category': 'Project Management',
    'description': """
This module adds 
        A additional tab for notes in task.
        A new npg projects portal user group 
        Makes Project required field on Task
        Modifies mails to move link for document in OERP to top of email so not hidden when signature folders in 
        email client

===================================================
    """,
    'author': 'NovaPoint Group LLC',
    'website': 'http://www.novapointgroup.com',
    'depends': ['project','project_gtd','portal_project','project_issue'],
    'data': [ 'security/portal_security.xml',
              'security/ir.model.access.csv',
             'project_task.xml',
             'task_sequence.xml',
             'project_task_menus.xml',
             'wizard/hr_timesheet_working_hours_wizard.xml',
             ],
             
    'js': [
        'static/src/js/npg_list_view_button.js',
    ],
    
#     'qweb' : [
#         "static/src/xml/npg_account_list_inherit.xml",
#     ],
    'demo': [],
    'installable': True,
    'auto_install': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
