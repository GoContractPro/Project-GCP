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
                wdtl += wline.work_note and ('\nWork Detail : ' + wline.work_note) or ''
                al.append(wdtl)
            desc = "\n\n===================================================\n\n".join(al)
            if vals.get('description'):
                vals['description'] += '\n' + desc
            else: vals['description'] = desc
        
        return super(task, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if len(ids) >1 : return super(task, self).write(cr, uid, ids, vals, context=context)
         
        if vals.get('work_ids'):
            desc = ''
            al = []
            prev_obj = self.browse(cr,uid,ids[0],context)
            for wrk in vals.get('work_ids'):
                wrk_line = wrk[2]
                if not wrk_line : continue
                wdtl = ""
                if wrk_line.get('hours'):
                    time_spent = ''
                    hrs = wrk_line['hours']   #wline.hours
                    h = math.floor(hrs)
                    m = (hrs-h)*60
                    
                    wdtl += 'Update Date : ' + time.strftime('%Y-%m-%d') #wline.date
                    wdtl += '\tTime Spent : ' + str(int(h))+':'+str(int(m))
                    
                wdtl += '\tUpdated by : ' + self.pool.get('res.users').browse(cr,uid,uid).name #wline.user_id.name
                summ = ''
                if wrk_line.get('name'):
                    summ = wrk_line['name'] or '' 
#                 else:
#                     summ = self.pool.get('').
                wdtl += '\nSummary : ' + summ
                wdtl += wline.work_note and ('\nWork Detail : ' + wline.work_note) or ''
                al.append(wdtl)
            desc = "\n\n===================================================\n\n".join(al)
            if vals.get('description'):
                vals['description'] += '\n\n===================================================\n\n' + desc
            else: 
                old_desc = prev_obj.description or ''
                vals['description'] = old_desc + '\n\n===================================================\n\n' + desc
        return super(task, self).write(cr, uid, ids, vals, context=context)

    
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

    



    