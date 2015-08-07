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
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _

class project_parent_selection(osv.osv_memory):
    _name='project.parent.selection'
    _columns={
              'parent_id':fields.many2one('project.task','Parent Task '),
              }
    
    def create_delegate(self, cr, uid, ids, context=None):
        
        '''This function is used to update the parent ids with the given existing parent id'''
        
        if context is None:
            context = {}
        task_id = context.get('active_id', False)
        project_task_obj = self.pool.get('project.task')
        self_brw = self.browse(cr,uid,ids[0])
        project_task_id = project_task_obj.search(cr,uid,[('id','=',self_brw.parent_id.id)])
        project_task_obj.write(cr,uid,task_id,{'parent_ids': [(6, 0, project_task_id)]})
        return True
