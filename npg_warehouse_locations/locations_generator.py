# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2004-2010 Verts Services India Pvt. Ltd.
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

from datetime import datetime, timedelta
from openerp.osv import fields, osv
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import string

class locations_generator(osv.osv):
    _name = "locations.generator"
    _rec_name = "parent_location"
    _columns = {
                'parent_location':fields.many2one('stock.location', 'Parent Location', select=True,required=True),
                'aisle_code_type':fields.selection([('char','Character'),('int','integer')],string="Aisle code type",required=True),
                'aisle_no_digits':fields.integer("Aisle no of Digits",required=True),
                'aisle_starting_code':fields.char("Aisle Starting Code",size=2,required=True),
                'aisle_ending_code':fields.char("Aisle Ending Code",size=2,required=True),
                
                'rack_code_type':fields.selection([('char','Character'),('int','integer')],string="Rack code type",required=True),
                'rack_no_digits':fields.integer("Rack no of Digits",required=True),
                'rack_starting_code':fields.char("Rack Starting Code",size=2,required=True),
                'rack_ending_code':fields.char("Rack Ending Code",size=2,required=True),
                
                'shelf_code_type':fields.selection([('char','Character'),('int','integer')],string="Shelf code type",required=True),
                'shelf_no_digits':fields.integer("Shelf no of Digits",required=True),
                'shelf_starting_code':fields.char("Shelf Starting Code",size=2,required=True),
                'shelf_ending_code':fields.char("Shelf Ending Code",size=2,required=True),
                
                'skip':fields.boolean("Skip Existings"),
                
                'temp_locs' : fields.text("Locations")
                
                }
    
    _defaults = {
                'aisle_code_type':'char',
                'aisle_no_digits':1,
                
                'rack_code_type':'int',
                'rack_no_digits':1,
               
                'shelf_code_type':'char',
                'shelf_no_digits':1,
                
                'skip':True
                 }

    def _check_codes(self, cr, uid, ids, context=None):
        alpha_codes = list(string.uppercase)
        for record in self.browse(cr, uid, ids, context=context):
            #===================================================================
            # Validation code For Aisle
            #===================================================================
            a_st = record.aisle_starting_code or ''
            a_end = record.aisle_ending_code or ''
           
            if record.aisle_code_type=='int':
                if not (a_st.isdigit() and a_end.isdigit()):
                    raise osv.except_osv(_('Error'), _('Both Aisle starting and ending code should be Numeric!'))
                if int(a_st) >= int(a_end):
                    raise osv.except_osv(_('Error'), _('Aisle starting code should be less than ending code!'))
            else:
                if not(a_st.upper() in alpha_codes and a_end.upper() in alpha_codes):
                    raise osv.except_osv(_('Error'), _('Both Aisle starting and ending code should be between A to Z!'))
                
                a_st_no = alpha_codes.index(a_st.upper())
                a_end_no = alpha_codes.index(a_end.upper())
                
                if a_end_no <= a_st_no:
                    raise osv.except_osv(_('Error'), _('Aisle starting and Ending codes should be in alphabetical order!'))
            #===================================================================
            # Validation code for Racks
            #===================================================================
            r_st = record.rack_starting_code or ''
            r_end = record.rack_ending_code or ''
            
            if record.rack_code_type=='int':
                if not (r_st.isdigit() and r_end.isdigit()):
                    raise osv.except_osv(_('Error'), _('Both Rack starting and ending code should be Numeric!'))
                if int(r_st) >= int(r_end):
                    raise osv.except_osv(_('Error'), _('Rack starting code should be less than ending code!'))
            else:
                if not(r_st.upper() in alpha_codes and r_end.upper() in alpha_codes):
                    raise osv.except_osv(_('Error'), _('Both Rack starting and ending code should be between A to Z!'))
                
                r_st_no = alpha_codes.index(r_st.upper())
                r_end_no = alpha_codes.index(r_end.upper())
                
                if r_end_no <= r_st_no:
                    raise osv.except_osv(_('Error'), _('Rack starting and Ending codes should be in alphabetical order!'))
                
            #===================================================================
            # Validation code for Shelfs
            #===================================================================
            s_st = record.shelf_starting_code or ''
            s_end = record.shelf_ending_code or ''
            
            if record.shelf_code_type=='int':
                if not (s_st.isdigit() and s_end.isdigit()):
                    raise osv.except_osv(_('Error'), _('Both shelf starting and ending code should be Numeric!'))
                if int(s_st) >= int(s_end):
                    raise osv.except_osv(_('Error'), _('Shelf starting code should be less than ending code!'))
            else:
                if not(s_st.upper() in alpha_codes and s_end.upper() in alpha_codes):
                    raise osv.except_osv(_('Error'), _('Both Shelf starting and ending code should be between A to Z!'))
                
                s_st_no = alpha_codes.index(s_st.upper())
                s_end_no = alpha_codes.index(s_end.upper())
                
                if s_end_no <= s_st_no:
                    raise osv.except_osv(_('Error'), _('Shelf starting and Ending codes should be in alphabetical order!'))
        return True

    _constraints = [
        (_check_codes, 'You cannot insert wrong codes format.',
            ['aisle_code_type','rack_code_type', 'shelf_code_type']),
        ]

    def button_generate_locations(self,cr, uid, ids, context={}):
        alpha_codes = list(string.uppercase)
        for gen in self.browse(cr, uid, ids, context):
            locations = []
            if gen.aisle_code_type == 'char':
                ac = gen.aisle_starting_code
                ae = gen.aisle_ending_code
                a_start = alpha_codes.index(ac.upper())
                a_end = alpha_codes.index(ae.upper())
            else:
                a_start = int(gen.aisle_starting_code)
                a_end = int(gen.aisle_ending_code)
            for asl in range(a_start, a_end+1):
                aisle = gen.aisle_code_type == 'char' and alpha_codes[asl] or asl
                if gen.rack_code_type == 'char':
                    rc = gen.rack_starting_code
                    re = gen.rack_ending_code
                    r_start = alpha_codes.index(rc.upper())
                    r_end = alpha_codes.index(re.upper())
                else:
                    r_start = int(gen.rack_starting_code)
                    r_end = int(gen.rack_ending_code)
                for rc in range(r_start, r_end+1):
                    rack = gen.rack_code_type == 'char' and alpha_codes[rc] or rc
                    if gen.shelf_code_type == 'char':
                        sc = gen.shelf_starting_code
                        se = gen.shelf_ending_code
                        s_start = alpha_codes.index(sc.upper())
                        s_end = alpha_codes.index(se.upper())
                    else:
                        s_start = int(gen.shelf_starting_code)
                        s_end = int(gen.shelf_ending_code)
                    for slf in range(s_start, s_end+1):
                        shelf = gen.shelf_code_type == 'char' and alpha_codes[slf] or slf
                        loc = str(aisle) +  str(rack) + str(shelf)
                        locations.append(loc)
                        
            temp_locs = ', '.join(locations)
            self.write(cr,uid,gen.id,{'temp_locs':temp_locs})
        return True
locations_generator()  


