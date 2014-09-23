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
        a additional tab for notes in task.
        working hours by Date form
        corrects issue with task created without project when project assigned creates analytic reocord

===================================================
    """,
    'author': 'NovaPoint Group LLC',
    'website': 'http://www.novapointgroup.com',
    'depends': ['project', 'hr_timesheet','project_gtd'],
    'data': ['project_task.xml',
             'task_sequence.xml',
             'project_task_menus.xml',
             'wizard/hr_timesheet_working_hours_wizard.xml'],
    'demo': [],
    'installable': True,
    'auto_install': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
