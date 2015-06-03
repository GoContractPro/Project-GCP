# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Stephen Levenhagen
#    Copyright 2015 NovapointGroup.com
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
from openerp import SUPERUSER_ID
from datetime import datetime, timedelta, date
import time

from openerp.tools.translate import _

class project_task_timesheet(osv.osv):
    
    _name = "project.task.timesheet"
    _table = "project_task_timesheet"   
    _inherits = {'hr.analytic.timesheet':'hr_analytic_timesheet_id'}
    _description = "Timesheet Task Line"
    _order = "id desc"
    _columns = {
            'hr_analytic_timesheet_id': fields.many2one('hr.analytic.timesheet', 'Timesheet Line', ondelete='cascade', required=True),
            'task_id':fields.many2one('project.task','Task',  required=True, ondelete='cascade', select=True,),
#            'public_note': fields.text('Public Notes'),
            'work_note': fields.text('Task Work Notes'),

    }
    
    _defaults = {
        'plan_time_amt':1.0,
        'user_id': lambda obj, cr, uid, context: uid,
        'plan_date_start': lambda *a: fields.datetime.now(),
        'state': 'planned'
        }

    def create(self, cr, uid, vals, *args, **kwargs):
        context = kwargs.get('context', {})
        
        
        return super(project_task_timesheet,self).create(cr, uid, vals, *args, **kwargs)

    
    def default_get(self, cr, uid, fields, context=None):
        
        res = super(project_task_timesheet, self).default_get(cr, uid, fields, context)
          
        if context is None:
            context = {}
            return res
        
        acc_id = False
        if context.get('task_project',False):
            project_obj = self.pool['project.project'].browse(cr, uid, context['task_project'], context=context)
            acc_id = project_obj and project_obj.analytic_account_id.id or False
            if acc_id:res['account_id'] = acc_id   
            
        return res
    
    def _getGeneralAccount(self, cr, uid, context=None):
        emp_obj = self.pool.get('hr.employee')
        if context is None:
            context = {}
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', context.get('user_id') or uid)], context=context)
        if emp_id:
            emp = emp_obj.browse(cr, uid, emp_id[0], context=context)
            if bool(emp.product_id):
                a = emp.product_id.property_account_expense.id
                if not a:
                    a = emp.product_id.categ_id.property_account_expense_categ.id
                if a:
                    return a
        return False

    def _getAnalyticJournal(self, cr, uid, context=None):
        emp_obj = self.pool.get('hr.employee')
        if context is None:
            context = {}
        if context.get('employee_id'):
            emp_id = [context.get('employee_id')]
        else:
            emp_id = emp_obj.search(cr, uid, [('user_id','=',context.get('user_id') or uid)], limit=1, context=context)
        if not emp_id:
            raise osv.except_osv(_('Warning!'), _('Please create an employee for this user, using the menu: Human Resources > Employees.'))
        emp = emp_obj.browse(cr, uid, emp_id[0], context=context)
        if emp.journal_id:
            return emp.journal_id.id
        else :
            raise osv.except_osv(_('Warning!'), _('No analytic journal defined for \'%s\'.\nYou should assign an analytic journal on the employee form.')%(emp.name))
    
    def _getEmployeeProduct(self, cr, uid, context=None):
        if context is None:
            context = {}
        emp_obj = self.pool.get('hr.employee')
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', context.get('user_id') or uid)], context=context)
        if emp_id:
            emp = emp_obj.browse(cr, uid, emp_id[0], context=context)
            if emp.product_id:
                return emp.product_id.id
        return False

    def _getEmployeeUnit(self, cr, uid, context=None):
        emp_obj = self.pool.get('hr.employee')
        if context is None:
            context = {}
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', context.get('user_id') or uid)], context=context)
        if emp_id:
            emp = emp_obj.browse(cr, uid, emp_id[0], context=context)
            if emp.product_id:
                return emp.product_id.uom_id.id
        return False
    
    
    def on_change_user_id(self, cr, uid, ids, user_id):
        if not user_id:
            return {}
        context = {'user_id': user_id}
        return {'value': {
            'product_id': self. _getEmployeeProduct(cr, uid, context),
            'product_uom_id': self._getEmployeeUnit(cr, uid, context),
            'general_account_id': self._getGeneralAccount(cr, uid, context),
            'journal_id': self._getAnalyticJournal(cr, uid, context),
            'account_id':1829,
        }}

    def on_change_date(self, cr, uid, ids, date):
        if ids:
            new_date = self.read(cr, uid, ids[0], ['date'])['date']
            if date != new_date:
                warning = {'title':'User Alert!','message':'Changing the date will let this entry appear in the timesheet of the new date.'}
                return {'value':{},'warning':warning}
        return {'value':{}}


    def on_change_plan_date_start(self, cr, uid, ids,plan_date_start,context):
        
        date1 = datetime.strptime(plan_date_start,"%Y-%m-%d %H:%M:%S")
        date_tz = fields.datetime.context_timestamp(cr,uid,date1,context=context)
        ret_date = date_tz.strftime("%Y-%m-%d")
        return {'value': {'date': ret_date} }
    
    def on_change_unit_amount(
            self, cr, uid, sheet_id, prod_id, unit_amount, company_id,
            unit=False, journal_id=False, to_invoice=False,
            context={}):
        hat_obj = self.pool.get("hr.analytic.timesheet")
        
        res = hat_obj.on_change_unit_amount(
            cr, uid, sheet_id, prod_id, unit_amount, company_id, unit,
            journal_id, context=context)
        print "context",context
        project_id = context.get('task_project')
        task_id = context.get('task_id')
        if 'value' in res and (task_id or project_id):
            if task_id:
                task_obj = self.pool['project.task']
                p = task_obj.browse(cr, uid, task_id,
                                    context=context).project_id
            elif project_id:
                p = self.pool['project.project'].browse(
                    cr, uid, project_id, context=context)
            if p:
                res['value']['account_id'] = p.analytic_account_id.id
                if p.to_invoice and not to_invoice:
                    res['value']['to_invoice'] = p.to_invoice.id
        print res
        return res   
        
        
        
    def on_change_task_id(self, cr, uid, ids , task_id, context = {}):
        proj = context.get('task_project')
        print "context", context
        print "task", task_id
        if not (task_id or proj):return {}
        prj = self.pool.get('project.project').browse(cr,uid,proj,context=context)
        if prj.analytic_account_id:
            return {'value': {'account_id': prj.analytic_account_id.id, 'analy_test': prj.analytic_account_id.id} }
        res = self.pool.get('project.task').browse(cr,uid,task_id,context=context)
        if res.project_id.analytic_account_id:
            return {'value': {'account_id': res.project_id.analytic_account_id.id} }
        return {}

    
    def _check_task_project(self, cr, uid, ids):
        for line in self.browse(cr, uid, ids):
            if line.task_id and line.account_id:
                if line.task_id.project_id.analytic_account_id.id != \
                        line.account_id.id:
                    return False
        return True
   
    def _trigger_projects(self, cr, uid, task_ids, context=None):
        t_obj = self.pool['project.task']
        for task in t_obj.browse(cr, SUPERUSER_ID, task_ids, context=context):
            project = task.project_id
            project.write({'parent_id': project.parent_id.id})
        return task_ids

    def _set_remaining_hours_create(self, cr, uid, vals, context=None):
        if not vals.get('task_id'):
            return
        hours = vals.get('unit_amount', 0.0)
        # We can not do a write else we will have a recursion error
        cr.execute(
            'UPDATE project_task '
            'SET remaining_hours=remaining_hours - %s '
            'WHERE id=%s', (hours, vals['task_id']))
        self._trigger_projects(cr, uid, [vals['task_id']], context=context)
        return vals
    
    def _set_remaining_hours_write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        for line in self.browse(cr, uid, ids):
            # in OpenERP if we set a value to nil vals become False
            old_task_id = line.task_id and line.task_id.id or None
            # if no task_id in vals we assume it is equal to old
            new_task_id = vals.get('task_id', old_task_id)
            # we look if value has changed
            if (new_task_id != old_task_id) and old_task_id:
                self._set_remaining_hours_unlink(cr, uid, [line.id], context)
                if new_task_id:
                    data = {'task_id': new_task_id,
                            'to_invoice': vals.get('to_invoice',
                                                   line.to_invoice.id),
                            'unit_amount': vals.get('unit_amount',
                                                    line.unit_amount)}
                    self._set_remaining_hours_create(cr, uid, data, context)
                    self._trigger_projects(
                        cr, uid, list(set([old_task_id, new_task_id])),
                        context=context)
                return ids
            if new_task_id:
                hours = vals.get('unit_amount', line.unit_amount)
                old_hours = line.unit_amount if old_task_id else 0.0
                # We can not do a write else we will have a recursion error
                cr.execute(
                    'UPDATE project_task '
                    'SET remaining_hours=remaining_hours - %s + (%s) '
                    'WHERE id=%s', (hours, old_hours, new_task_id))
                self._trigger_projects(cr, uid, [new_task_id], context=context)
        return ids

    def _set_remaining_hours_unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        for line in self.browse(cr, uid, ids):
            if not line.task_id:
                continue
            hours = line.unit_amount or 0.0
            cr.execute(
                'UPDATE project_task '
                'SET remaining_hours=remaining_hours + %s '
                'WHERE id=%s', (hours, line.task_id.id))
        return ids
      
    _constraints = [
        (_check_task_project, _('Error! Task must belong to the project.'),
         ['task_id', 'account_id']),
    ]

    
    def init(self, cr):
        
        cr.execute("""insert into public.project_task_timesheet 
        (task_id, hr_analytic_timesheet_id,create_date,create_uid)
        
        SELECT 
          tw.task_id,
          tw.hr_analytic_timesheet_id,
          tw.create_date,
          tw.create_uid
        
        FROM 
          public.project_task_work tw, 
          public.hr_analytic_timesheet ts
          
           
        WHERE 
          tw.hr_analytic_timesheet_id = ts.id and 
          tw.hr_analytic_timesheet_id not in (
          Select hr_analytic_timesheet_id 
          FROM 
            project_task_timesheet)""")
                
        cr.execute("""update public.account_analytic_line a
        set name = d.name
        FROM 
        (SELECT 
          project_task_work.name,
          account_analytic_line.id

        FROM 
          public.project_task_work, 
          public.project_task_timesheet,
          public.hr_analytic_timesheet,
          public.account_analytic_line
        WHERE 
          project_task_work.hr_analytic_timesheet_id  = project_task_timesheet.hr_analytic_timesheet_id AND
          project_task_timesheet.hr_analytic_timesheet_id = hr_analytic_timesheet.id AND
          hr_analytic_timesheet.line_id = account_analytic_line.id
          and project_task_work.name is not null AND
          project_task_timesheet.task_id is null) d
         where a.id = d.id""")
    

class project_task(osv.osv):
    _inherit = "project.task"
    _name = "project.task"

    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        """TODO improve code taken for OpenERP"""
        res = {}
        cr.execute("""SELECT ptt.task_id, COALESCE(SUM(aal.unit_amount),0)
                        FROM project_task_timesheet ptt ,
                            hr_analytic_timesheet hat,
                            account_analytic_line aal
                      WHERE task_id IN %s AND
                           ptt.hr_analytic_timesheet_id = hat.id AND
                           hat.line_id = aal.id
                      GROUP BY task_id""", (tuple(ids),))
        hours = dict(cr.fetchall())
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = {}
            res[task.id]['effective_hours'] = hours.get(task.id, 0.0)
            res[task.id]['total_hours'] = (
                task.remaining_hours or 0.0) + hours.get(task.id, 0.0)
            res[task.id]['delay_hours'] = res[task.id][
                'total_hours'] - task.planned_hours
            res[task.id]['progress'] = 0.0
            if (task.remaining_hours + hours.get(task.id, 0.0)):
                res[task.id]['progress'] = round(
                    min(100.0 * hours.get(task.id, 0.0) /
                        res[task.id]['total_hours'], 99.99), 2)
            if task.state in ('done', 'cancelled'):
                res[task.id]['progress'] = 100.0
        return res

    def _store_set_values(self, cr, uid, ids, field_list, context=None):
        # Hack to avoid redefining most of function fields of project.project
        # model. This is mainly due to the fact that orm _store_set_values use
        # direct access to database. So when modify a line the
        # _store_set_values as it uses cursor directly to update tasks
        # project triggers on task are not called
        res = super(project_task, self)._store_set_values(
            cr, uid, ids, field_list, context=context)
        for row in self.browse(cr, SUPERUSER_ID, ids, context=context):
            if row.project_id:
                project = row.project_id
                project.write({'parent_id': project.parent_id.id})
        return res
    
    
    def _hours_get(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        cr.execute("""SELECT ptt.task_id, COALESCE(SUM(aal.unit_amount),0)
                        FROM project_task_timesheet ptt ,
                            hr_analytic_timesheet hat,
                            account_analytic_line aal
                      WHERE task_id IN %s AND
                           ptt.hr_analytic_timesheet_id = hat.id AND
                           hat.line_id = aal.id
                      GROUP BY task_id""",(tuple(ids),))
        hours = dict(cr.fetchall())
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = {'effective_hours': hours.get(task.id, 0.0), 'total_hours': (task.remaining_hours or 0.0) + hours.get(task.id, 0.0)}
            res[task.id]['delay_hours'] = res[task.id]['total_hours'] - task.planned_hours
            res[task.id]['progress'] = 0.0
            if (task.remaining_hours + hours.get(task.id, 0.0)):
                res[task.id]['progress'] = round(min(100.0 * hours.get(task.id, 0.0) / res[task.id]['total_hours'], 99.99),2)
            if task.state in ('done','cancelled'):
                res[task.id]['progress'] = 100.0
        return res
    
    def _get_task(self, cr, uid, ids, context=None):
        result = {}
        for work in self.pool.get('project.task.timesheet').browse(cr, uid, ids, context=context):
            if work.task_id: result[work.task_id.id] = True
        return result.keys()
    
    _columns = {
        'sheet_ids' : fields.one2many('project.task.timesheet', 'task_id', 'Work Lines', ),      
                
        'effective_hours': fields.function(_hours_get, string='Hours Spent', multi='hours', help="Computed using the sum of the task work done.",
            store = {
                'project.task': (lambda self, cr, uid, ids, c={}: ids, ['work_ids', 'remaining_hours', 'planned_hours'], 10),
                'project.task.timesheet': (_get_task, ['hours'], 10),
            }),
       
        'total_hours': fields.function(_hours_get, string='Total', multi='hours', help="Computed as: Time Spent + Remaining Time.",
            store = {
                'project.task': (lambda self, cr, uid, ids, c={}: ids, ['work_ids', 'remaining_hours', 'planned_hours'], 10),
                'project.task.timesheet': (_get_task, ['hours'], 10),
            }),
        'progress': fields.function(_hours_get, string='Progress (%)', multi='hours', group_operator="avg", help="If the task has a progress of 99.99% you should close the task if it's finished or reevaluate the time",
            store = {
                'project.task': (lambda self, cr, uid, ids, c={}: ids, ['work_ids', 'remaining_hours', 'planned_hours', 'state', 'stage_id'], 10),
                'project.task.timesheet': (_get_task, ['hours'], 10),
            }),
        'delay_hours': fields.function(_hours_get, string='Delay Hours', multi='hours', help="Computed as difference between planned hours by the project manager and the total hours of the task.",
            store = {
                'project.task': (lambda self, cr, uid, ids, c={}: ids, ['work_ids', 'remaining_hours', 'planned_hours'], 10),
                'project.task.timesheet': (_get_task, ['hours'], 10),
            }),        
    }
    

    def write(self, cr, uid, ids, vals, context=None):
        res = super(project_task, self).write(
            cr, uid, ids, vals, context=context)
        if vals.get('project_id'):
            ts_obj = self.pool.get('project.task.timesheet')
            project_obj = self.pool.get('project.project')
            project = project_obj.browse(
                cr, uid, vals['project_id'], context=context)
            account_id = project.analytic_account_id.id
            for task in self.browse(cr, uid, ids, context=context):
                ts_obj.write(cr, uid, [ts.id for ts in task.sheet_ids],
                             {'account_id': account_id}, context=context)
        return res

''' 
class AccountAnalyticLine(osv.osv):
    
    _inherit = "account.analytic.line"


   def create(self, cr, uid, vals, context=None):
        if vals.get('task_id'):
            self._set_remaining_hours_create(cr, uid, vals, context)
        return super(AccountAnalyticLine, self).create(cr, uid, vals,
                                                       context=context)

    def write(self, cr, uid, ids, vals, context=None):
        self._set_remaining_hours_write(cr, uid, ids, vals, context=context)
        return super(AccountAnalyticLine, self).write(cr, uid, ids, vals,
                                                      context=context)

    def unlink(self, cr, uid, ids, context=None):
        self._set_remaining_hours_unlink(cr, uid, ids, context)
        return super(AccountAnalyticLine, self).unlink(cr, uid, ids,
                                                       context=context) '''


