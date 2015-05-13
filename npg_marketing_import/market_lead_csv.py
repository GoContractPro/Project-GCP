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
import time

import logging

_logger = logging.getLogger(__name__)

class market_lead_csv(osv.osv_memory):
    _name = 'marketing.lead.csv'
    _columns = {
        'name':fields.char('Started',size=10, readonly=True),
        'end_time': fields.datetime('End',  readonly=True),
        'browse_path': fields.binary('Csv File Path'),
        'error_log': fields.text('Error Log'),
    }
 #   _defaults = {
 #                'name' :time.strftime('%Y-%m-%d %H:%M:%S'),
 #                }
    def import_csv(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        state_obj = self.pool.get('res.country.state')
        start = time.strftime('%Y-%m-%d %H:%M:%S')
        if context is None:
            context = {}
        for wiz_rec in self.browse(cr, uid, ids, context=context):
            
            str_data = base64.decodestring(wiz_rec.browse_path)
            if not str_data:
                raise osv.except_osv('Warning', 'The file contains no data')
            try:
                partner_data = list(csv.reader(cStringIO.StringIO(str_data)))
            except:
                raise osv.except_osv('Warning', 'Make sure you saved the file as .csv extension and import!')
            

            headers_list = []
            for header in partner_data[0]:
                headers_list.append(header.strip())
            headers_dict = {
                'x_first_name': headers_list.index('FName'),
                'x_last_name': headers_list.index('LName'),
                'email'     : headers_list.index('Email'),
                'street': headers_list.index('Address'),
                'city': headers_list.index('City'),
                'x_county': headers_list.index('County'),
                'state_code': headers_list.index('State'),
                'zip':headers_list.index('Zip'),
                'x_averagehousevalue' :headers_list.index('AverageHouseValue'),
                'x_income'  :headers_list.index('IncomePerHousehold'),
                
                
                
            }
            
            error_log = ''
            for data in partner_data[1:]:
                
                state_search_val = [('code','=',data[headers_dict['state_code']])] 
                
                part_vals = {
                        'name'          :data[headers_dict['x_first_name']] + ' ' + data[headers_dict['x_last_name']],
                        'email'         :data[headers_dict['email']],
                        'x_first_name'  :data[headers_dict['x_first_name']],
                        'x_last_name'   :data[headers_dict['x_last_name']],
                        'street'        :data[headers_dict['street']],
                        'city'          :data[headers_dict['city']],
                        'x_county'      :data[headers_dict['x_county']],
                        'state_id'      :state_obj.search(cr, uid , state_search_val)[0] or None,
                        'zip'           :data[headers_dict['zip']],
                        'x_averagehousevalue': data[headers_dict['x_averagehousevalue']],
                        'x_income'      :data[headers_dict['x_income']], 
                        'x_marketing': True,                                 
                        }
                search = [ ('email','=', part_vals.get('email', False))]
                part_id = partner_obj.search(cr,uid,search) or None
                if part_id:
                    continue
                
                
                try:
                    partner_obj.create(cr, uid,part_vals , context=context)
                except:
                    _logger.info('Error  # partner not created for %s',data[headers_dict['Name']])
                    error_log += ('Error ' + data[headers_dict['Name']] + ', ' + data[headers_dict['Street']])
                    
            vals = {'name':start,
                    'end_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'error':error_log}
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
