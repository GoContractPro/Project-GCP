# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp import netsvc


class hr_timesheet_sheet(osv.osv):
    
    _inherit = "hr_timesheet_sheet.sheet"
    
    def get_latest_sheet_date_to(self,cr,uid,user,context=None):
        
        cr.execute('SELECT max(date_to) \
                        FROM  hr_timesheet_sheet_sheet\
                        WHERE  user_id=%s ',(user,))
        c=(cr.fetchone())[0]
        
        if c:
            return c
        return False

    def _default_date_from(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        
        last_date_to= self.get_latest_sheet_date_to(cr,uid, uid, context=context)
        
        if last_date_to:
            date_from = (datetime.strptime(last_date_to, '%Y-%m-%d')+ relativedelta( days=1)).strftime('%Y-%m-%d')
            return date_from
        r = user.company_id and user.company_id.timesheet_range or 'month'
        if r=='month':
            return time.strftime('%Y-%m-01')
        elif r=='week':
            return (datetime.today() + relativedelta(weekday=0, days=-6)).strftime('%Y-%m-%d')
        elif r=='year':
            return time.strftime('%Y-01-01')
        return time.strftime('%Y-%m-%d')
    
    _columns ={
               'date_from': fields.date('Date from', required=True, select=1, readonly=True, 
                        states={'draft': [('readonly', False)],'new':[('readonly', False)]}),
               'date_to': fields.date('Date to', required=True, select=1, readonly=True, 
                        states={'draft': [('readonly', False)],'new':[('readonly', False)]}),
               }
    
    _defaults = {
                 'date_from' : _default_date_from,
                }
class hr_timesheet_line(osv.osv):
    _inherit = "hr.analytic.timesheet"

    def _sheet(self, cursor, user, ids, name, args, context=None):
        sheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
        res = {}.fromkeys(ids, False)
        for ts_line in self.browse(cursor, user, ids, context=context):
            sheet_ids = sheet_obj.search(cursor, user,
                [('date_to', '>=', ts_line.date), ('date_from', '<=', ts_line.date),
                 ('employee_id.user_id', '=', ts_line.user_id.id),
                 ('state', 'in', ['draft', 'new'])],
                context=context)
            if sheet_ids:
            # [0] because only one sheet possible for an employee between 2 dates
                res[ts_line.id] = sheet_obj.name_get(cursor, user, sheet_ids, context=context)[0]
        return res

    def _get_hr_timesheet_sheet(self, cr, uid, ids, context=None):
        ts_line_ids = []
        for ts in self.browse(cr, uid, ids, context=context):
            cr.execute("""
                    SELECT l.id
                        FROM hr_analytic_timesheet l
                    INNER JOIN account_analytic_line al
                        ON (l.line_id = al.id)
                    WHERE %(date_to)s >= al.date
                        AND %(date_from)s <= al.date
                        AND %(user_id)s = al.user_id
                    GROUP BY l.id""", {'date_from': ts.date_from,
                                        'date_to': ts.date_to,
                                        'user_id': ts.employee_id.user_id.id,})
            ts_line_ids.extend([row[0] for row in cr.fetchall()])
        return ts_line_ids

    def _get_account_analytic_line(self, cr, uid, ids, context=None):
        ts_line_ids = self.pool.get('hr.analytic.timesheet').search(cr, uid, [('line_id', 'in', ids)])
        return ts_line_ids

    _columns = {
                'sheet_id': fields.function(_sheet, string='Sheet', select="1",
                type='many2one', relation='hr_timesheet_sheet.sheet', 
                store={
                        'hr_timesheet_sheet.sheet': (_get_hr_timesheet_sheet, ['employee_id', 'date_from', 'date_to'], 10),
                        'account.analytic.line': (_get_account_analytic_line, ['user_id', 'date'], 10),
                        'hr.analytic.timesheet': (lambda self,cr,uid,ids,context=None: ids, None, 10),
                      },
                ),
                }

