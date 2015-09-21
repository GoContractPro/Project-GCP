# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
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
    'name':'sync data',
    'version':'1.0',
    'category':'sync data detail',
    'description': """
    This module adds customizations import projects and tasks from external Database.
    """,
    'author':'Novapoint Group Inc, Stephen Levenhagen',
    'website':'www.novapointgroup.com',
    'data':['wizard/sync_data_info.xml'],
    'depends':['base'],
    'auto_install':False,
    'installable':True,
    'active':True
}
