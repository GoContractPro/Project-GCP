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

    def button_generate_locations(self,cr, uid, ids, context={}):
        alpha_codes = list(string.uppercase)
        for gen in self.browse(cr, uid, ids, context):
            locations = []
            if gen.aisle_code_type == 'char':
                a_start = alpha_codes.index(gen.aisle_starting_code)
                a_end = alpha_codes.index(gen.aisle_ending_code)
            else:
                a_start = int(gen.aisle_starting_code)
                a_end = int(gen.aisle_ending_code)
            for asl in range(a_start, a_end+1):
                aisle = gen.aisle_code_type == 'char' and alpha_codes[asl] or asl
                if gen.rack_code_type == 'char':
                    r_start = alpha_codes.index(gen.rack_starting_code)
                    r_end = alpha_codes.index(gen.rack_ending_code)
                else:
                    r_start = int(gen.rack_starting_code)
                    r_end = int(gen.rack_ending_code)
                for rc in range(r_start, r_end+1):
                    rack = gen.rack_code_type == 'char' and alpha_codes[rc] or rc
                    if gen.shelf_code_type == 'char':
                        s_start = alpha_codes.index(gen.shelf_starting_code)
                        s_end = alpha_codes.index(gen.shelf_ending_code)
                    else:
                        s_start = int(gen.shelf_starting_code)
                        s_end = int(gen.shelf_ending_code)
                    for slf in range(s_start, s_end+1):
                        shelf = gen.shelf_code_type == 'char' and alpha_codes[slf] or slf
                        loc = str(aisle) +  str(rack) + str(shelf)
                        locations.append(loc)
        return True
locations_generator()  


