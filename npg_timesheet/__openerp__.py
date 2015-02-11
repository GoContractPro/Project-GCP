# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2015 NovaPoint Group INC (<http://www.novapointgroup.com>)
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
    'name': 'NPG Timesheet Enhancement',
    'version': '1.0',
    'category': '',
    "sequence": 14,
    'complexity': "medium",
    'category': 'Time Sheet',
    'description': """
NovaPoint Group Inc Enhancements Functionality of Time Sheets Lines

* Calendar views for time Sheet lines
* Wizard to search for working hours over date range and by user
* Planed Start Date & Time for planned Task work
* Time sheet line Statuses
* Buttons to log starting work, pausing work, finishing work
* Auto create new time sheet line copy if restarting work on new day
* Auto sign in attendance when starting any work
* Auto Pause any work if signed out of attendance
* Auto Pause any current Timesheet line which is being worked on if starting work non new time sheet line
* Allow  linking Timesheet entries to any Document 

        
    """,
    'author': 'NovaPoint Group Inc, Stephen Levenhagen',
    'website': 'www.novapointgroup.com',
    'depends': ["base","npg_warning","hr_timesheet","npg_project"],
    'init_xml': [],
    'data': [
        "views/timesheet_view.xml",
        "views/menus.xml",
        "timesheet_workflow.xml",
        "wizard/hr_timesheet_working_hours_wizard.xml"
    ],
    'demo_xml': [],
    'test': [
    ],
    'qweb' : [
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
