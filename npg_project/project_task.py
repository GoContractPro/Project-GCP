# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools
import math

class task(osv.osv):
    _name = "project.task"
    _inherit = ["project.task"]
    _columns = {
    'task_number':fields.char('Task Number', size=32),
	'pub_descrip': fields.text('Public Notes'),
    }

           
    def create(self, cr, uid, vals, context=None):
        if vals.get('task_number',0) == 0:
            vals['task_number'] = self.pool.get('ir.sequence').get(cr, uid, 'project.task') or '/'
            
        if vals.get('work_ids'):
            desc = ''
            al = []
            for wrk in vals.get('work_ids'):
                time_spent = ''
                hrs = wrk[2]['hours']   #wline.hours
                h = math.floor(hrs)
                m = (hrs-h)*60
                wdtl = ""
                wdtl += 'Date : ' + wrk[2]['date'] #wline.date
                wdtl += '\tTime Spent : ' + str(int(h))+':'+str(int(m))
                wdtl += '\tDone by : ' + self.pool.get('res.users').browse(cr,uid,wrk[2]['user_id']).name #wline.user_id.name
                wdtl += '\nSummary : ' + wrk[2]['name'] or '' #(wline.name or '')
     #           wdtl += wline.wrk_dtl and ('\nWork Detail : ' + wline.wrk_dtl) or ''
                al.append(wdtl)
            desc = "\n\n===================================================\n\n".join(al)
            if vals.get('description'):
                vals['description'] += '\n' + desc
            else: vals['description'] = desc
        return super(task, self).create(cr, uid, vals, context=context)
    
    #===========================================================================
    # def write(self, cr, uid, ids, vals, context=None):
    #     
    #     
    #     if vals.get('work_ids'):
    #         desc = ''
    #         al = []
    #         for wrk in vals.get('work_ids'):
    #             if not wrk[2] and wrk[2]['name'] : continue
    #             #===============================================================
    #             # time_spent = ''
    #             # hrs = wrk[2]['hours']   #wline.hours
    #             # h = math.floor(hrs)
    #             # m = (hrs-h)*60
    #             wdtl = ""
    #             # wdtl += 'Date : ' + wrk[2]['date'] #wline.date
    #             # wdtl += '\tTime Spent : ' + str(int(h))+':'+str(int(m))
    #             # wdtl += '\tDone by : ' + self.pool.get('res.users').browse(cr,uid,wrk[2]['user_id']).name #wline.user_id.name
    #             #===============================================================
    #             wdtl += '\nSummary : ' + wrk[2]['name'] or '' #(wline.name or '')
    #  #           wdtl += wline.wrk_dtl and ('\nWork Detail : ' + wline.wrk_dtl) or ''
    #             al.append(wdtl)
    #         desc = "\n\n===================================================\n\n".join(al)
    #         if vals.get('description'):
    #             vals['description'] += '\n' + desc
    #         else: vals['description'] = desc
    #     return super(task, self).write(cr, uid, ids, vals, context=context)
    #===========================================================================
    
#===============================================================================
# class hr_timesheet_line(osv.osv):
#     _inherit = "hr.analytic.timesheet"
#     
#     _columns = {
#                 'search_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="Search from"),
#                 'search_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="Search to"),
#                  }
#===============================================================================

    



    