# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 NovaPoint Group LLC (<http://www.novapointgroup.com>)
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
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
import pytz
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
import time

class hr_analytic_timesheet(osv.osv):
 
    _inherit = "hr.analytic.timesheet"

    def _name_get_resname(self, cr, uid, ids, object, method, context):
        data = {}
        for attachment in self.browse(cr, uid, ids, context=context):
            model_object = attachment.res_model
            res_id = attachment.res_id
            if model_object and res_id:
                model_pool = self.pool.get(model_object)
                res = model_pool.name_get(cr,uid,[res_id],context)
                res_name = res and res[0][1] or False
                if res_name:
                    field = self._columns.get('res_name',False)
                    if field and len(res_name) > field.size:
                        res_name = res_name[:field.size-3] + '...' 
                data[attachment.id] = res_name
            else:
                data[attachment.id] = False
        return data
    _columns = {
        'plan_date_start': fields.datetime('Scheduled Start'),
        'date_start':fields.datetime('Actual Start'),
        'plan_time_amt': fields.float('Planned Time', select="1"),
        'state': fields.selection([('planned','Planned'),('cancel','Cancelled'),('pause','Paused'),('working', 'Working'),('done','Finished')],'Status', readonly=False,
               help="* When a Timesheet Activity is created  with Scheduled Start Time it is set in 'Planned' status.\n" \
                     "* When user sets Timesheet Activity in start mode that time it will be set in 'In Progress' status and time start time will be updated to current time\n" \
                     "* When Timesheet Activity is in running mode, during that time if user wants to stop counting time for task then can set in 'Pending' working time is updated .\n" \
                     "* When the user cancels Timesheet Activity it will be set in 'Canceled' status.\n" \
                     "* When Timesheet Activity is completed time it is set in 'Finished' status. and working time is updated"),
        'log_ids':  fields.one2many('hr.analytic.timesheet.log','timesheet_id','Status Logs', readonly=True),
        'res_name': fields.function(_name_get_resname, type='char', size=128, string='Resource Name', store=True),
        'res_model': fields.char('Resource Model',size=64, readonly=True, help="The database object this attachment will be attached to"),
        'res_id': fields.integer('Resource ID', readonly=True, help="The record id this is attached to"),
        'search_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="Search from"),
        'search_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="Search to"),
        
        'date_finished': fields.datetime('Finished Date'),
        }
    
    _defaults = {
        'plan_time_amt':1.0,
        'user_id': lambda obj, cr, uid, context: uid,
        'plan_date_start': lambda *a: fields.datetime.now(),
        'state': 'planned'
        }


    def on_change_plan_date_start(self, cr, uid, ids,plan_date_start,context):
        
        date1 = datetime.strptime(plan_date_start,"%Y-%m-%d %H:%M:%S")
        date_tz = fields.datetime.context_timestamp(cr,uid,date1,context=context)
        ret_date = date_tz.strftime("%Y-%m-%d")
        return {'value': {'date': ret_date} }
    
    def action_planned(self, cr, uid, ids, context=None):
        """ Sets state to planned.
        @return: True
        """
        return self.write(cr, uid, ids, {'state': 'planned'}, context=context)

    def _check_working(self, cr, uid, ids, context=None):
        """ Check working lines and pause them.
        @return: True
        """
        return True
    
    def date_to_datetime(self, cr, uid, userdate, context=None):
        user_date = datetime.strptime(userdate, '%Y-%m-%d %H:%M:%S')
        if context and context.get('tz'):
            tz_name = context['tz']
        else:
            tz_name = self.pool.get('res.users').read(cr, SUPERUSER_ID, uid, ['tz'])['tz']
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            user_datetime = user_date #- relativedelta(hours=5.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime('%Y-%m-%d %H:%M:%S')
        return user_date.strftime('%Y-%m-%d %H:%M:%S')

    def action_start_working(self, cr, uid, ids, context=None):
        """ Sets state to working and writes starting date.
        @return: True
        """
        self.create_status_log(cr, uid,  ids[0],'working', context)
        date_now = time.strftime('%Y-%m-%d %H:%M:%S')
        date = date_now[:10]
        emp_obj = self.pool.get('hr.employee')
        att_date=datetime.now()
        att_date=(datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        for sheet in self.browse(cr,uid,ids):
            user_id=sheet.user_id.id
            emp_id=emp_obj.search(cr, uid, [('user_id','=',user_id)])
            if emp_id:
                eobj=emp_obj.browse(cr,uid,emp_id[0])
                emp_state=eobj.state
                if emp_state=='absent':
                    emp_obj.attendance_action_change(cr, uid, emp_id, {'action':'sign_in', 'action_date':att_date})
            if user_id:
                active_timesheet_lines=self.pool.get('hr.analytic.timesheet').search(cr, uid, [('user_id','=',user_id),('state','=','working'),('id','!=',sheet.id)])
                for id in active_timesheet_lines:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'hr.analytic.timesheet', id, 'button_pause', cr)
        self.write(cr, uid, ids, {'state':'working', 'date_start': date_now, 'date':date}, context=context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        """ Sets state to done, writes finish date and calculates delay.
        @return: True
        """
        time_now = datetime.now()
        obj_line = self.browse(cr, uid, ids[0])
        emp_obj = self.pool.get('hr.employee')
        start_time = self.get_latest_status_log(cr,uid,ids[0],context=context)    
        work_time_hours = (time_now - start_time).total_seconds()/ float(60*60)
        work_time_hours = work_time_hours#round(work_time_hours/.25)*.25
        amount = obj_line.unit_amount + work_time_hours
        
        att_date=datetime.now()
        att_date=(datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        for sheet in self.browse(cr,uid,ids):
            user_id=sheet.user_id.id
            emp_id=emp_obj.search(cr, uid, [('user_id','=',user_id)])
            if emp_id:
                eobj=emp_obj.browse(cr,uid,emp_id[0])
                emp_state=eobj.state
                if emp_state=='present':
                    emp_obj.attendance_action_change(cr, uid, emp_id, {'action':'sign_out', 'action_date':att_date})
        date_finished = datetime.strftime(time_now,'%Y-%m-%d %H:%M:%S')
        self.create_status_log(cr, uid,  ids[0],'done', context)
        self.write(cr, uid, ids, {'state':'done', 'date_finished': date_finished,'unit_amount':amount}, context=context)

        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Sets state to cancel.
        @return: True
        """
        self.create_status_log(cr, uid,  ids[0],'cancel', context)
        return self.write(cr, uid, ids, {'state':'cancel'}, context=context)

    def action_pause(self, cr, uid, ids, context=None):
        """ Sets state to pause.
        @return: True
        """
        emp_obj = self.pool.get('hr.employee')
        time_now = datetime.now()
        
        start_time = self.get_latest_status_log(cr,uid,ids[0],context=context)
        
        work_time_hours = (time_now - start_time).seconds / float(60*60)
        work_time_hours = work_time_hours #round(work_time_hours/.25)*.25
        att_date=datetime.now()
        att_date=(datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        for line in self.browse(cr,uid,ids, context=context):
            user_id=line.user_id.id
            emp_id=emp_obj.search(cr, uid, [('user_id','=',user_id)])
            if emp_id:
                eobj=emp_obj.browse(cr,uid,emp_id[0])
                emp_state=eobj.state
                if emp_state=='present':
                    emp_obj.attendance_action_change(cr, uid, emp_id, {'action':'sign_out', 'action_date':att_date})
            amount = line.unit_amount + work_time_hours
        self.create_status_log(cr, uid,  ids[0],'pause', context)
        return self.write(cr, uid, ids, {'state':'pause','unit_amount':amount }, context=context)

    def action_resume(self, cr, uid, ids, context=None):
        """ Sets state to working.@return: True"""
        """ If is a new day create copy of the timesheet line """
        id = ids[0]
        pause_time = self.get_latest_status_log(cr, uid, id, 'pause', context)
        day_paused =pause_time.strftime('%Y%j')
        day_now = time.strftime('%Y%j')
        emp_obj = self.pool.get('hr.employee')
        date_now = time.strftime('%Y-%m-%d %H:%M:%S')
        att_date=datetime.now()
        att_date=(datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        if day_paused <> day_now:
            date = time.strftime("%Y-%m-%d")
            new_id = self.copy(cr, uid, id, default={'unit_amount':0,'date':date,'state':'working'}, context=context)
            self.create_status_log(cr, uid,  id,'working', context)
            return self.pool.get('warning').info(cr, uid, title='New Timesheet Line',message= "Restarting work on a new day created a new time sheet line")
        self.create_status_log(cr, uid,  id,'working', context)
        for sheet in self.browse(cr,uid,ids):
            user_id=sheet.user_id.id
            emp_id=emp_obj.search(cr, uid, [('user_id','=',user_id)])
            if emp_id:
                eobj=emp_obj.browse(cr,uid,emp_id[0])
                emp_state=eobj.state
                if emp_state=='absent':
                    emp_obj.attendance_action_change(cr, uid, emp_id, {'action':'sign_in', 'action_date':att_date})
            if user_id:
                active_timesheet_lines=self.pool.get('hr.analytic.timesheet').search(cr, uid, [('user_id','=',user_id),('state','=','working'),('id','!=',sheet.id)])
                for id in active_timesheet_lines:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'hr.analytic.timesheet', id, 'button_pause', cr)
        return self.write(cr, uid, ids, {'state':'working'}, context=context)
    
    def create_status_log(self, cr, uid, timesheet_id, state, context=None):
        
        logs = self.pool.get('hr.analytic.timesheet.log')
        vals = {'status':state,
                'timesheet_id':timesheet_id,
                }
        logs.create(cr, uid , vals , context=context)
        
        
    def get_latest_status_log(self,cr,uid,timesheet_id,state='working',context=None):
        
        cr.execute(''' SELECT max(create_date) 
                        FROM hr_analytic_timesheet_log
                        WHERE status = %s 
                        AND timesheet_id = %s ''',(state,timesheet_id))
        c=(cr.fetchone())[0]
        if c:
            c = c.split('.')[0]
            latest_time = datetime.strptime(c, "%Y-%m-%d %H:%M:%S")
        
        return latest_time
    
class hr_analytic_timesheet_log(osv.osv):

    _name = 'hr.analytic.timesheet.log'
    _description = 'Logs timestamps of timesheet line status changes'
    _columns = {
                'status': fields.char('Status', size=64, translate=True, required=True),
                'timesheet_id': fields.many2one('hr.analytic.timesheet', 'Timesheet Reference', 
                                required=True, ondelete='cascade', select=True, readonly=True, ),
                                
                }                
                