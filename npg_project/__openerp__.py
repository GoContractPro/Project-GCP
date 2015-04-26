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
        Project Functionality Enhancements
        ==================================
            * Additional tab for notes on tasks.
            * A new Projects Portal user group 
            * Add field for Task Number sequence Field
            * Project is made as required field on Task
            * New simplified Project menu removes kanbans as default view on tasks
            * My Task opens group by Project 
            * All Task opens in list view group by Projects
            * Enhances Issues Form for Portal Users
            *             
        
        ===================================================
    """,
    'author': 'NovaPoint Group LLC',
    'website': 'http://www.novapointgroup.com',

    'depends': ['project',
                'project_gtd',
                'portal_project',
                'project_issue',
                'project_timesheet',
                'hr_timesheet','hr_timesheet_sheet'],

    'data': [ 'security/portal_security.xml',
              'security/ir.model.access.csv',
             'task_sequence.xml',
             'views/project_task_views.xml',
             'views/issues_views.xml',
             'views/project_view.xml',
             'views/project_task_menus.xml',             
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
