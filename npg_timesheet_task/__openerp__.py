# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Stephen Levenhagen
#    Copyright 2015 Novapoint Group, INC
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
{'name': 'Analytic Timesheet In Task',
 'version': '0.2.1',
 'author': ' Novapoint Group , Stephen Levenhagen,  Camptocamp',
 'maintainer': 'Novappoint Group Inc USA',
 'category': 'Human Resources',
 'depends': ['project', 'npg_project','npg_timesheet','project_timesheet',],
 'description': """
adapted from Replaces task work items (project.task.work) linked to task with
timesheet lines (hr.analytic.timesheet).

Unless the module project_timesheet, it allows to have only one single
object that handles and records time spent by employees, making more
coherence for the end user. This way, time entered through timesheet
lines or tasks is the same. As long as a timesheet lines has an
associated task, it will compute the related indicators.

Used with the module hr_timesheet_task, it also allows users to complete
task information through the timesheet sheet (hr.timesheet.sheet). 'website': 'http://novapointgroup.com',
    """,
 'website': 'http://novapointgroup.com ',
 'data':[ 
         'project_task_view.xml',
          'menus.xml',
          "security/ir.model.access.csv",
          ],
 'demo': [],
 'test': ['test/task_timesheet_indicators.yml'],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True,
 }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
