# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools
import math

class task(osv.osv):
    _name = "project.task"
    _inherit = ["project.task"]

    def _get_work_dtl(self, cr, uid, ids, fields, args, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            al = []
            for wline in task.work_ids:
                time_spent = ''
                hrs = wline.hours
                h = math.floor(hrs)
                m = (hrs-h)*60
                wdtl = ""
                wdtl += 'Date : ' + wline.date
                wdtl += '\tTime Spent : ' + str(int(h))+':'+str(int(m))
                wdtl += '\tDone by : ' + wline.user_id.name
                wdtl += '\nSummary : ' + (wline.name or '')
                wdtl += wline.wrk_dtl and ('\nWork Detail : ' + wline.wrk_dtl) or ''
                al.append(wdtl)
            res[task.id] = "\n\n===================================================\n\n".join(al)
        return res
    
    _columns = {
    'task_number':fields.char('Task Number', size=32),
	'pub_descrip': fields.text('Public Notes'),
    'work_details': fields.function(_get_work_dtl,string="Work Log Details",type="text",),
    }

           
    def create(self, cr, uid, vals, context=None):
        if vals.get('task_number',0) == 0:
            vals['task_number'] = self.pool.get('ir.sequence').get(cr, uid, 'project.task') or '/'
        return super(task, self).create(cr, uid, vals, context=context)
    
class project_work(osv.osv):
    _inherit = "project.task.work"
    _columns = {
                'wrk_dtl':fields.text("Work Details"),
                } 
    _defaults = {
                 'wrk_dtl':'',
                 }




    