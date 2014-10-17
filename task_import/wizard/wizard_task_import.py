# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
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

from openerp.osv import osv, fields
import csv
import cStringIO
import base64
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

class task_read_csv(osv.osv_memory):
    _name = 'task.read.csv'
    _columns = {
        'browse_path': fields.binary('Csv File Path'),
    }

    def import_csv(self, cr, uid, ids, context=None):
        task_obj = self.pool.get('project.task')
        proj_obj = self.pool.get('project.project')
        if context is None:
            context = {}
        for wiz_rec in self.browse(cr, uid, ids, context=context):
            task_vals = {}
            str_data = base64.decodestring(wiz_rec.browse_path)
            if not str_data:
                raise osv.except_osv('Warning', 'The file contains no data')
            try:
                task_data = list(csv.reader(cStringIO.StringIO(str_data)))
            except:
                raise osv.except_osv('Warning', 'Make sure you saved the file as .csv extension and import!')
            
            headers_list = []
            for header in bom_data[0]:
                headers_list.append(header.strip())
            headers_dict = {
                'parent': headers_list.index('Parent'),
                'child': headers_list.index("Child"),
                'qty': headers_list.index('Qty'),
            }
            
            for data in task_data[1:]:
                parent = data[headers_dict['parent']]
                child = data[headers_dict['child']]
                qty = data[headers_dict['qty']]
                if parent in task_vals:
                    task_vals[parent].append((child, qty))
                else:
                    task_vals.update({parent: [(child, qty)]})
            for key, vals in task_vals.iteritems():
                pass
            
                

        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
