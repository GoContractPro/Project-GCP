# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools

class task(osv.osv):
    
    _inherit = "project.task"
    _columns = {
    'task_number':fields.char('Task Number', size=32),
	'pub_descrip': fields.text('Public Notes'),
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
    
class project_work(osv.osv):
    _inherit = "project.task.work"
    
    _columns = {
                'work_note': fields.text('Task Work Notes')
                }

class project_issue(osv.osv):
    
    _inherit = "project.issue"
    
    _columns = {
                'logged_by_id': fields.many2one('res.users', 'Created By', required=False, select=1,
                         track_visibility='onchange'),
                'project_id': fields.many2one('project.project', 'Project', 
                        track_visibility='onchange', select=True,required=True ),
       
                }
    
    def _get_partner_contact(self, cr, uid, context=None):
        
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user and user.partner_id:
            return user.partner_id.id
        return super(project_issue, self)._get_partner_contact(cr, uid, context=context)

    
    _defaults = {
                 'user_id': False,
                 'logged_by_id' :lambda obj, cr, uid, context: uid,
                 'partner_id': lambda s, cr, uid, c: s._get_partner_contact(cr, uid, c),
                 }

    



    