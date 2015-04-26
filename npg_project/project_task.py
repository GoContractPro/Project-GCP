# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools
import math
import time


class task(osv.osv):
    
    _inherit = "project.task"
    _columns = {
    'task_number':fields.char('Task Number', size=32),
	'pub_descrip': fields.text('Public Notes'),
    'work_notes' : fields.text('Work Items Log'),
    }

           
    def create(self, cr, uid, vals, context=None):
        if vals.get('task_number',0) == 0:
            vals['task_number'] = self.pool.get('ir.sequence').get(cr, uid, 'project.task') or '/'
                    
        return super(task, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if len(ids) >1 : return super(task, self).write(cr, uid, ids, vals, context=context)
         
# create a log of the task Work Updates in project.task work_notes        
        if vals.get('work_ids'):
            desc = ''
            al = []
            prev_work_obj = self.browse(cr,uid,ids[0],context)
            work_line_obj = self.pool.get("project.task.work")
            separator = "\n\t----------------------------------------------------\n"
            separator2 = "=====================================================================================================\n"
            for wrk in vals.get('work_ids'):
                wrk_line = wrk[2]
                
                if not wrk_line : continue
                
                if wrk[1]:
                    prev_work_line = work_line_obj.browse(cr,uid,wrk[1],context)
                    updated = '   (*Revised*)'
                    wdtl = '\t **Task Work Line Revised**\n'
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
                
                if 'hours' in wrk_line:
                    hrs = wrk_line['hours'] or 0 
                    wdtl += '\tHours : %s ' % hrs + updated + '\n'
                else:
                    hrs = (prev_work_line and prev_work_line.hours) or 0 
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
            vals['work_notes'] +=   separator + desc or ''
            vals['work_notes'] += '\n' + prev_work_obj.work_notes or ''
            
        return super(task, self).write(cr, uid, ids, vals, context=context) 
    

class project_work(osv.osv):
    _inherit = "project.task.work"
    
    _columns = {
                'work_note': fields.text('Task Work Notes'),
                }

    
    def action_task_work_line_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        
        work_line_obj = self.browse(cr,uid,ids[0],context=context)
        
        task_id = work_line_obj.task_id.id or False
        task_obj = self.pool.get('project.task').browse(cr,uid,task_id,context)
        separator= "----------------------------------------------------<br>"

        wdtl = '<br>' + separator 
        summary = work_line_obj.name or''

        wdtl += 'Work Summary : ' + summary + '<br>' or ''
                            
        if  work_line_obj.user_id.id:
            done_by_name = self.pool.get('res.users').browse(cr,uid,work_line_obj.user_id.id).name or ''
            
        wdtl += 'Done By : ' + done_by_name + '<br>' or ''
       
        wdtl += 'Date : %s ' % (work_line_obj.date or '') +'<br>'
 
        wdtl += 'Hours : %s ' % (work_line_obj.hours or 0) + '<br>'
        
        wdtl += separator

        wdtl += '<br>Detail :' '<br>' + (work_line_obj.work_note or ''+ '<br>') or ''

        subject = 'Re:'+ task_obj.name + 'Work Summary : ' + summary + '<br>' or ''
        
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'project.task',
            'default_res_id': task_id,
            'default_body': wdtl,
            'default_subject':subject,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'mail_post_autofollow': True,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        
        

    
