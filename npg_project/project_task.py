# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.osv import fields, osv

class task(osv.osv):
    _name = "project.task"
    _inherit = ["project.task",'pad.common']
    _columns = {
    'task_number':fields.integer('Task Number'),
	'pub_descrip': fields.text('Public Notes'),
    'public_pad': fields.char('Public PAD', pad_content_field='pub_descrip'),
    }


            
    def create(self, cr, uid, vals, context=None):
        if vals.get('task_number',0) == 0:
            vals['task_number'] = self.pool.get('ir.sequence').get(cr, uid, 'project.task') or '/'
        return super(task, self).create(cr, uid, vals, context=context)
    
class hr_timesheet_line(osv.osv):
    _inherit = "hr.analytic.timesheet"
    
    _columns = {
                'search_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="Search from"),
                'search_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="Search to"),
                 }