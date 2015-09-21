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

class project_task_timesheet(osv.osv):
    _inherit = "project.task.timesheet"
    
    
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
 
        wdtl += 'Hours : %s ' % (work_line_obj.unit_amount or 0) + '<br>'
        
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
        