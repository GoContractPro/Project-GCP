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
    'name': 'Project Task Work Notes',
    'version': '1.0',
    'category': '',
    'complexity': "easy",
    'category': 'Generic Modules/Others',
    'description': """
        * Adds new field "Work Notes" to Project Task Work lines.
        * Pop Up form to enter Task Work Line
        * Adds new page on "Task" form called "Work Log". 
            Work log is updated  each time a Task work line is added or updated. This in effect 
            keeps a permanent history of changes made to Work History, also gives a easy to read 
            and review format for work history.
            
        
        
    """,
    'author': 'NovaPoint Group Inc, Stephen Levenhagen',
    'website': 'www.novapointgroup.com',
    'depends': ['project','npg_timesheet_task'],
    'init_xml': [],
    'data': [
        "views/project_task_view.xml",
        ],
    'demo_xml': [],
    'test': [],
    'qweb' : [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
