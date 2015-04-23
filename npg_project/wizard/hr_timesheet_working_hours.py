# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_timesheet_working_hours(osv.osv_memory):
    _name = 'hr.timesheet.working.hours'
    _description = 'hr.timesheet.working.hours'
    _columns = {
        'from_date': fields.date('From'),
        'to_date': fields.date('To'),
        'user_id': fields.many2one('res.users','user_id','Employee')
        }

    def open_working_hours(self, cr, uid,ids, context=None):

        mod_obj =self.pool.get('ir.model.data')
        domain = []
        data = self.read(cr, uid, ids, [])[0]
        from_date = data['from_date']
        to_date = data['to_date']
        user = data['user_id']
        
        if from_date and to_date:
            domain = [('date','>=',from_date), ('date','<=',to_date)]
        elif from_date:
            domain = [('date','>=',from_date)]
        elif to_date:
            domain = [('date','<=',to_date)]
            
        if user:
            domain.append(('user_id','=',user[0]))
#        result = mod_obj.get_object_reference(cr, uid, 'timesheet_task', 'act_hr_timesheet_lines_form')
#        id = result and result[1] or False
        return {
              'name': _('Working Time by date'),
              'view_type': 'form',
              "view_mode": 'tree,form',
              'res_model': 'hr.analytic.timesheet',
              'type': 'ir.actions.act_window',
              'domain': domain,
              }
        
    def recreate_deleted_analytic_entries(self, cr, uid,ids, context=None):
        
        timesheet_obj = self.pool.get('hr.analytic.timesheet')
        taskwork_obj = self.pool.get('project.task.work')

        data = self.read(cr, uid, ids, [])[0]
        from_date = data['from_date']
        to_date = data['to_date']
        user = data['user_id']
        
        domain = [('hr_analytic_timesheet_id','=',False)]
        
        
        if from_date and to_date:
            domain.append(('date','>=',from_date + ' 00:00:00'))
            domain.append(('date','<=',to_date + ' 23:59:59'))
        elif from_date:
            domain.append(('date','>=',from_date + ' 00:00:00'))
        elif to_date:
            domain.append(('date','<=',to_date + ' 23:59:59'))
            
        if user:
            domain.append(('user_id','=',user[0]))
        
        
        
        work_ids = taskwork_obj.search(cr,uid, domain, context = context)

        for work_id in work_ids:
     
            vals = taskwork_obj.copy_data(cr, uid, work_id, default=None, context=None)
            timeline_id = taskwork_obj._create_analytic_entries(cr, uid, vals, context)  
            taskwork_obj.write(cr, uid, work_id, {'hr_analytic_timesheet_id' : timeline_id}, context=context)
  
    
        return

hr_timesheet_working_hours()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
