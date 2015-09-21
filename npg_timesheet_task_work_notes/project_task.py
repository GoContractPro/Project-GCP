# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 NovaPoint Group INC (<http://www.novapointgroup.com>)
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


from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
from openerp import netsvc
from datetime import datetime, timedelta
import math
import time

class task(osv.osv):
    
    _inherit = "project.task"
    _columns = {'work_notes' : fields.text('Work Items Log'),
                }
    
    def create(self, cr, uid, vals, context=None):
        
        if not vals.get('work_ids')  : return super(task, self).create(cr, uid, vals, context=context)
        vals = self.generate_task_work_log(cr, uid,False,vals,context)
        return super(task, self).create(cr, uid,  vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        
        if len(ids) >1 : return super(task, self).write(cr, uid, ids, vals, context=context)
        task_id = ids[0]
        vals = self.generate_task_work_log(cr, uid, task_id, vals, context)
        return super(task, self).write(cr, uid, ids, vals, context=context)      
# create a log of the task Work Updates in project.task work_notes 
    def generate_task_work_log(self,cr,uid,task_id,vals,context):       
        if vals.get('sheet_ids'):
            desc = ''
            al = []
            if task_id:
                prev_work_obj = self.browse(cr,uid,task_id,context)
            else:
                prev_work_obj = False
                
            work_line_obj = self.pool.get("project.task.timesheet")
            separator = "\n\t--------------------------------------------------------------\n"
            separator2 = "==================================================================================================\n"
            for wrk in vals.get('sheet_ids'):
                wrk_line = wrk[2]
                
                if not wrk_line : continue
                
                if wrk[1]:
                    prev_work_line = work_line_obj.browse(cr,uid,wrk[1],context)
                    updated = '   (*Revised*)'
                    wdtl = '\t **Task Work Line [%s] Revised**\n' % wrk[1]
                else:
                    prev_work_line = False
                    updated = ''
                    wdtl = ''
           
                if 'name' in wrk_line:
                    summ = wrk_line['name'] or '' 
                    wdtl += '\tWork Line Summary : ' + summ + updated +'\n' or ''
                    
                else:
                    summ = (prev_work_line and prev_work_line.name) or '' 
                    wdtl += '\tWork Line Summary : ' + summ + '\n' or ''
                                
                if  'user_id' in wrk_line:
                    done_by_id = wrk_line['name'] or False
                    done_by_name = done_by_id and self.pool.get('res.users').browse(cr,uid,done_by_id).name or ''
                    wdtl += '\tDone By : ' + done_by_name +  updated + '\n' or ''
            
                else:
                    done_by_id = (prev_work_line and prev_work_line.user_id.id) or False 
                    done_by_name = done_by_id and self.pool.get('res.users').browse(cr,uid,done_by_id).name or ''
                    wdtl += '\tDone By : ' + done_by_name + '\n' or ''
                
                if 'date' in wrk_line:
                    date = wrk_line['date'] or '' 
                    wdtl += '\tDate : %s ' % date + updated + '\n'
                else:
                    date =  (prev_work_line and prev_work_line.date) or '' 
                    wdtl += '\tDate : %s \n' % date    
                
                if 'unit_amount' in wrk_line:
                    hrs = wrk_line['unit_amount'] or 0 
                    wdtl += '\tHours : %s ' % hrs + updated + '\n'
                else:
                    hrs = (prev_work_line and prev_work_line.unit_amount) or 0 
                    wdtl += '\tHours : %s \n' % hrs                
                
                if 'work_note' in wrk_line:
                    note = wrk_line['work_note'] or False
                    wdtl +=  (note and'\n\nDetail :' + updated +'\n' + note + '\n') or ''
                else:
                    note = (prev_work_line and prev_work_line.work_note) or False  
                    wdtl += (note and'\n\nDetail : \n' + note + '\n') or ''
                
                
                al.append(wdtl)
                
            desc = separator.join(al)
#            if vals.get('work_notes'):
            update_by =self.pool.get('res.users').browse(cr,uid,uid).name 
            
            vals['work_notes'] = separator2
            vals['work_notes'] += '   Task Work Update by ' + update_by + ' at ' + time.strftime('%Y-%m-%d %H:%M:%S') + '  \n'
            vals['work_notes'] += separator2
            vals['work_notes'] += desc or ''
            vals['work_notes'] += '\n' + (prev_work_obj and prev_work_obj.work_notes or '')
            
        return vals
    

class project_work(osv.osv):
    _inherit = "project.task.work"
    
    _columns = {
                'work_note': fields.text('Task Work Notes'),
                }
