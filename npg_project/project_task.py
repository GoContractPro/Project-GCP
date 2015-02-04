# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools

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
        return super(task, self).create(cr, uid, vals, context=context)
    

    



    