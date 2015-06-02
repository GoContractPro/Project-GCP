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


from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import csv
import cStringIO
import base64
from datetime import datetime
import time

import logging
import sys

_logger = logging.getLogger(__name__)

HEADER_MAP = {


                'email'     : 'Email',
                'street': 'Address',
                'city': 'City',
                
                'x_first_name':'FName',
                'x_last_name':'LName',
                'x_county': 'County',
                'state_code':'State',
                'zip':'Zip',
                'x_averagehousevalue' :'AverageHouseValue',
                'x_income'  : 'IncomePerHousehold',
                'x_sic_code1' : 'sic_code',
                'x_sic_code_description': 'sic_code_description',
                'x_first_name' : 'first_name',
                'x_last_name'   :'last_name',
                'name' : 'contact_name',
                'x_title'     :'title',
                'company_name': 'company_name',
                'street':   'address',
                'phone':'phone',
                'x_revenue': 'revenue',
                'x_employees':'employees',
               
                }

def index_get(L, i, v=None):
    try: return L.index(i)
    except: return v

class partner_csv(osv.osv):
    _name = 'import.marketing.csv'
    _columns = {
        'name':fields.char('Started',size=10, readonly=True),
        'end_time': fields.datetime('End',  readonly=True),
        'browse_path': fields.binary('Csv File Path', required=True),
        'error_log': fields.text('Error Log'),
        'test_sample_size': fields.integer('Test Sample Size'),
        'do_update': fields.boolean('Allow Update', 
                help='If Set when  matching unique fields on records will update values for record, Otherwise will just log duplicate and skip this record '),
        'field_map' : fields.text ('Available Import Fields ', readonly = True, help='Display the CSV to Odoo Field map relations'),
        }
    
    
    def _get_header_map(self, cr, uid, context=None):
        field_map = 'CSV Column -->> Odoo Field \n\n'
        for field, column in HEADER_MAP.iteritems():
            field_map += column + ' -->> ' + field + '\n'
        return field_map
    
    _defaults = {
        'test_sample_size':20,
        'field_map' : _get_header_map
        
        }
    
    
    def check_expected_headers(self, cr, uid, ids, context=None):
         
        # Mapp Odoo Fields to  CSVColumns
        
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
            headers_dict ={}
            
            for header in partner_data[0]:
                headers_list.append(header.strip())
             
            msg = 'IF Position not listed then column is not found on CSV file \n\n'
            msg += 'Position  -- CSV Column -- Odoo field  \n\n'
            fields_matched = {}
            fields_missing = []  
            
            headers_list = [x.lower() for x in headers_list ] 
            for field, column in HEADER_MAP.iteritems():
                col_num = index_get(headers_list,column.lower())
                if col_num is None:
                    fields_missing.append(field)
                else:
                    fields_matched[col_num + 1] = (column + ' -- ' + field)

            fields_match_sort = sorted(fields_matched.keys()) 
             
            for position in fields_match_sort:  
                msg += str(position)  + ' -- ' + fields_matched[position]
                msg += '\n'
                
            msg += '\n'
            msg += 'Fields not found in Sheet --  \n\n'
            for fields in fields_missing:
                msg +=  fields + ', '
            
        
                
        popup_obj = self.pool.get( 'warning.warning')
        return popup_obj.info(cr, uid, title='CSV Map ', message = msg)
        
    
    
    def import_csv(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        state_obj = self.pool.get('res.country.state')
        country_obj = self.pool.get('res.country')
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
            headers_list = [x.lower() for x in headers_list ] 
             
            headers_dict = {}
            for field, column in HEADER_MAP.iteritems():  
                
                headers_dict[field] = index_get(headers_list,column.lower())
                
            error_log = ''
            n = 1 # Start Counter at One for to Account for Column Headers
            
            time_start = datetime.now()
            for data in partner_data[1:]:
                
                    n += 1
                    first = ((headers_dict.get('x_first_name') > -1) and data[headers_dict['x_first_name']]) or None
                    last = ((headers_dict.get('x_last_name') > -1) and data[headers_dict['x_last_name']]) or None
               
                    email =  ((headers_dict.get('email') > -1) and data[headers_dict['email']]) or None  
                    
                    name = ((headers_dict.get('name') > -1) and data[headers_dict['name']]) or None
                    
                    if not (email):
                        _logger.info(_('Missing Name and Email at Record %s \n' % (n, )))
                        error_log += _('Missing Name and Email at Record %s \n' % (n, ))
                        
                        continue 
                    skip = False
                    for search in ['admin@','support@','info@','sales@']:
                        found = email.find(search)
                        if found > -1: 
                            skip = True
                    if skip:
                        _logger.info(_('Skip (admin,support,sales or info)Email %s at Record %s \n' % (email,n, )))
                        error_log += _('Skip (admin,support,sales or info)Email %s at Record %s \n' % (email,n, ))
                        continue
                        
                    if  not name:
                        if first or last:
                            name =  '%s %s' %(first or '',last or '')
                        else: 
                            name = email                   
                       
                    search = [ ('email','=', email ),('is_company','=',False)]
                    partner_ids = partner_obj.search(cr,uid,search) or None
                    
                    if partner_ids and not wiz_rec.do_update:
                        _logger.info(_('Duplicate Found at Record %s -- %s, %s \n' % (n,name or '',email or'' )))
                        error_log += _('Duplicate Found at Record %s -- %s, %s \n' % (n,name or '',email or'' ))
                        
                        continue 
                    

                    
                    if (headers_dict.get('country_code') > -1) and data[headers_dict['country_code']]:
                       
                        
                        try: 
                            country_search_val = [('code','=',data[headers_dict['country_code']])]
                            country_id = country_obj.search(cr, uid , country_search_val)[0] or None
                        except:
                            msg = _('Error Country %s Not Found at Record %s -- %s, %s \n' % (data[headers_dict['country_code']],n,name or '',email or'' ))
                            _logger.info(msg)
                            error_log += msg
                            country_id = None
                    else:
                        # if no Country Code column Make Default US
                        country_id = country_obj.search(cr, uid , [('code','=','US')])[0]
                        
                    
                    if (headers_dict.get('state_code') > -1) and data[headers_dict['state_code']]:
                        try: 
#                           state_search_val = [('code','=',data[headers_dict['state_code']]),('country_id.code','=',headers_dict['country_code'] and data[headers_dict['country_code']] or 'US')]
                            state_search_val = [('code','=',data[headers_dict['state_code']]),('country_id','=',country_id)]
                            state_id = state_obj.search(cr, uid , state_search_val)[0] or None
                        except:
                            msg = _('Error State - %s - Not Found at Record %s -- %s, %s \n' % (data[headers_dict['state_code']],n,name or '',email or'' ))
                            _logger.info(msg)
                            error_log += msg
                            state_id = None
                    else:
                        state_id =  None
                            
                        
                    if (headers_dict.get('property_payment_term') > -1) and data[headers_dict['property_payment_term']]:
                        try:    
                            term_obj = self.pool.get('account.payment.term')
                            term_search = [('name','=',data[headers_dict['property_payment_term']])]
                            property_payment_term = term_obj.search(cr, uid , term_search)
                            property_payment_term = property_payment_term[0] or None
                        except:
                            msg = _('Error Payment Term - %s - Not Found at Record %s -- %s, %s \n' % (data[headers_dict['property_payment_term']],n,name or '',email or'' ))
                            _logger.info(msg)
                            error_log += msg
                            property_payment_term = None
                    else:
                        property_payment_term = None
                            
                    if (headers_dict.get('company_name') > -1) and data[headers_dict['company_name']]:
                        search = [('name','=',data[headers_dict['company_name']]),('is_company','=',True)]
                        parent_id = partner_obj.search(cr,uid,search)
                        if not parent_id:
                            vals = {'name':data[headers_dict['company_name']],
                                    'is_company': True,
                                    }
                            parent_id = partner_obj.create(cr,uid,vals,context)
                        else: parent_id = parent_id[0]                                      
                    try:
                        part_vals = {
                                'name'          :name,
                                'email'         :email,
                                'street'        :((headers_dict.get('street')>-1) and data[headers_dict['street']]) or None,
#                                'street2'       :headers_dict.get('street2') and data[headers_dict['street2']] or None,
                                'city'          :((headers_dict.get('city') > -1) and data[headers_dict['city']]) or None,
                                'country_id'    :country_id,
                                'state_id'      :state_id,                             
                                'zip'           :((headers_dict.get('zip') > -1) and data[headers_dict['zip']]) or None,
#                                'property_payment_term': property_payment_term,
#                               'is_company'    :headers_dict.get('is_company') and data[headers_dict['is_company']] or False,
#                                'employee'      :headers_dict.get('employee') and data[headers_dict['employee']] or False,
#                                'customer'      :headers_dict.get('customer') and data[headers_dict['customer']] or False ,
#                                'supplier'      :headers_dict.get'supplier') anif n == wiz_rec.test_sample_size  and context.get('test',True):
#                                'credit_limit'  :headers_dict.get('credit_limit') and data[headers_dict['credit_limit']] or None,
#                                'debit_limit'   :headers_dict.get('debit_limit') and data[headers_dict['debit_limit']] or None,
                                'parent_id'     :parent_id,
                                'phone'         :((headers_dict.get('phone') > -1) and data[headers_dict['phone']]) or None,
#                                'fax'           :headers_dict.get('fax') and data[headers_dict['fax']] or None,
#                                'mobile'        :headers_dict.get('mobile') and data[headers_dict['mobile']] or None,
#                                'website'       :headers_dict.get('website') and data[headers_dict['website']] or None, 
#                                'ref'           :headers_dict.get('ref') and data[headers_dict['ref']] or None,
#                                'comment'       :headers_dict.def('comment') and data[headers_dict['comment']] or None, 
                                'x_first_name':     ((headers_dict.get('x_first_name') > -1) and data[headers_dict['x_first_name']]) or None,
                                'x_last_name':      ((headers_dict.get('x_last_name') > -1) and data[headers_dict['x_last_name']]) or None,
                                'x_county':         ((headers_dict.get('x_county') > -1) and data[headers_dict['x_county']]) or None,
                                'x_averagehousevalue' :((headers_dict.get('x_averagehousevalue') > -1) and data[headers_dict['x_averagehousevalue']]) or None,
                                'x_income'  :           ((headers_dict.get('x_income') > -1) and data[headers_dict['x_income']]) or None,
                                'x_revenue'  :           ((headers_dict.get('x_revenue') > -1) and data[headers_dict['x_revenue']]) or None,
                                'x_sic_code1'  :           ((headers_dict.get('x_sic_code_1') > -1) and data[headers_dict['x_sic_code_1']]) or None,                   
                                'x_sic_code_description'  :((headers_dict.get('x_sic_code_description') > -1) and data[headers_dict['x_sic_code_description']]) or None,                   
                                'x_employees'  :           ((headers_dict.get('x_employees') > -1) and data[headers_dict['x_employees']]) or None,
                                'x_title'  :           ((headers_dict.get('x_title') > -1) and data[headers_dict['x_title']]) or None,
                                'x_marketing':     True,
                                'use_parent_address': False,
                                               
                                                  
                                }
                        
                                                
                        if partner_ids and wiz_rec.do_update:
                            partner_obj.write(cr, uid,partner_ids, part_vals)
                            _logger.info('update record %s for %s, %s ',n,name,email)
                        
                        else:
                            partner_obj.create(cr, uid,part_vals , context=context)
                            _logger.info('Loaded record %s for %s, %s ',n,name,email)
                        
                        #exit loop and Roll back updates if is a test
                        try:
                            if n == wiz_rec.test_sample_size  and context.get('test',False):
                                t2 = datetime.now()
                                time_delta = (t2 - time_start)
                                time_each = time_delta // wiz_rec.test_sample_size
                                list_size = len(partner_data)
                                 
                                estimate_time = (time_each * list_size)
                                
                                
                                msg = _('%s Total Records in Import, Estimated Import Time is %s (hrs:min:sec) \n\n %s' % (list_size, estimate_time ,error_log))
                                
                                cr.rollback()
                                vals = {'name':start,
                                'end_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'error_log':error_log}
                                self.write(cr,uid,ids[0],vals)
                                return self.show_warning(cr, uid, msg , context = context)
                        except:
                            e = sys.exc_info()
                            _logger.error(_('Error %s' % (e,)))
                            vals = {'error_log': e}
                            cr.rollback()
                            self.write(cr,uid,ids[0],vals)
                            return vals
                        
                    except:
                        
                        e = sys.exc_info()
                        _logger.info(_('Error  # partner not created for %s, %s' % (name or '',email or'' )))
                        error_log += _('Error  %s at Record %s -- %s, %s \n' % (e,n,name or '',email or'' ))
                        if n == wiz_rec.test_sample_size  and context.get('test',True):
                            vals = {'error_log': error_log}
                            cr.rollback()
                            self.write(cr,uid,ids[0],vals)
                            return vals
                    
        vals = {'name':start,
                'end_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'error_log':error_log}
        if context.get('test',False):
            cr.rollback()
        self.write(cr,uid,ids[0],vals)
        result = {} 
        result['value'] = vals   
        return result
    
    def show_message(self, cr, uid, ids, context=None):
        
        return self.show_warning(cr,uid, "this is test")
        
    def show_warning(self,cr,uid,msg="None",context=None):
        
        warn_obj = self.pool.get( 'warning.warning')
        return warn_obj.info(cr, uid, title='Import Information',message = msg)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
