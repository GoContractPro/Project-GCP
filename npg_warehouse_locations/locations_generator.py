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
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
                'parent_location':fields.many2one('stock.location', 'Parent Location', select=True,required=True,readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange'),
                'aisle_code_type':fields.selection([('char','Character'),('int','integer')],string="Aisle code type",required=True,readonly=True, states={'draft': [('readonly', False)]}),
                'aisle_no_digits':fields.selection([(1,'1'),(2,'2')],string="Aisle no of Digits",required=True,readonly=True, states={'draft': [('readonly', False)]}),#fields.integer("Aisle no of Digits",required=True),
                'aisle_starting_code':fields.char("Aisle Starting Code",size=2,required=True,readonly=True, states={'draft': [('readonly', False)]}),
                'aisle_ending_code':fields.char("Aisle Ending Code",size=2,required=True,readonly=True, states={'draft': [('readonly', False)]}),
                
                'rack_code_type':fields.selection([('char','Character'),('int','integer')],string="Rack code type",required=True,readonly=True, states={'draft': [('readonly', False)]}),
                'rack_no_digits':fields.selection([(1,'1'),(2,'2')],string="Rack no of Digits",required=True,readonly=True, states={'draft': [('readonly', False)]}),#fields.integer("Rack no of Digits",required=True),
                'rack_starting_code':fields.char("Rack Starting Code",size=2,required=True,readonly=True, states={'draft': [('readonly', False)]}),
                'rack_ending_code':fields.char("Rack Ending Code",size=2,required=True,readonly=True, states={'draft': [('readonly', False)]}),
                
                'shelf_code_type':fields.selection([('char','Character'),('int','integer')],string="Shelf code type",required=True,readonly=True, states={'draft': [('readonly', False)]}),
                'shelf_no_digits':fields.selection([(1,'1'),(2,'2')],string="Shelf no of Digits",required=True,readonly=True, states={'draft': [('readonly', False)]}),#fields.integer("Shelf no of Digits",required=True),
                'shelf_starting_code':fields.char("Shelf Starting Code",size=2,required=True,readonly=True, states={'draft': [('readonly', False)]}),
                'shelf_ending_code':fields.char("Shelf Ending Code",size=2,required=True,readonly=True, states={'draft': [('readonly', False)]}),
                
                'skip':fields.boolean("Skip Existings",readonly=True, states={'draft': [('readonly', False)]}),
                
                'temp_locs' : fields.text("Locations"),
                
                'state': fields.selection([('draft',"Draft"),('confirm',"Locations confirmed"),('done',"Generated"),],"State",track_visibility='onchange'),
                
                'generated_locations':fields.one2many('stock.location','gen_id',string="Locations", readonly=True)
                
                }
    
    _defaults = {
                'aisle_code_type':'char',
                'aisle_no_digits':1,
                
                'rack_code_type':'int',
                'rack_no_digits':1,
               
                'shelf_code_type':'char',
                'shelf_no_digits':1,
                
                'skip':True,
                
                'state':'draft'
                 }

    def _check_codes(self, cr, uid, ids, context=None):
        alpha_codes = list(string.uppercase)
        twoLetterSequence = ['-'+l for l in string.uppercase] + [ "%c%c" % (x, y) for x in range(ord('A'), ord('Z')+1) for y in range(ord('A'), ord('Z')+1)]
        for record in self.browse(cr, uid, ids, context=context):
            #===================================================================
            # Validation code For Aisle
            #===================================================================
            a_st = record.aisle_starting_code or ''
            a_end = record.aisle_ending_code or ''
           
            if record.aisle_code_type=='int':
                if not (a_st.isdigit() and a_end.isdigit()):
                    raise osv.except_osv(_('Warning'), _('Both Aisle starting and ending code should be Numeric!'))
                if int(a_st) >= int(a_end):
                    raise osv.except_osv(_('Warning'), _('Aisle starting code should be less than ending code!'))
                if int(record.aisle_no_digits) == 2 and (int(a_st)>99 or int(a_end)>99) or (int(a_st)<0 or int(a_end)<0):
                    raise osv.except_osv(_('Warning'), _('Both Aisle starting and ending code should be in range of 0 to 99!'))
                if int(record.aisle_no_digits) == 1 and (int(a_st)>9 or int(a_end)>9) or (int(a_st)<0 or int(a_end)<0):
                    raise osv.except_osv(_('Warning'), _('Both Aisle starting and ending code should be in range of 0 to 9!'))
            else:
                if int(record.aisle_no_digits) == 1:
                    if not(a_st.upper() in alpha_codes and a_end.upper() in alpha_codes):
                        raise osv.except_osv(_('Warning'), _('Both Aisle starting and ending code should be between A to Z!'))
                    
                    a_st_no = alpha_codes.index(a_st.upper())
                    a_end_no = alpha_codes.index(a_end.upper())
                    
                    if a_end_no <= a_st_no:
                        raise osv.except_osv(_('Warning'), _('Aisle starting and Ending codes should be in alphabetical order!'))
                else:
                    a_st = len(a_st) == 2 and a_st or '-'+ a_st
                    a_end = len(a_end) == 2 and a_end or '-'+ a_end
                    if not(a_st.upper() in twoLetterSequence and a_end.upper() in twoLetterSequence):
                        raise osv.except_osv(_('Warning'), _('Both Aisle starting and ending code should be between AA to ZZ. e.g. AA, AB, PA, XZ!'))
                    
                    a_st_no = twoLetterSequence.index(a_st.upper())
                    a_end_no = twoLetterSequence.index(a_end.upper())
                    
                    if a_end_no <= a_st_no:
                        raise osv.except_osv(_('Warning'), _('Aisle starting and Ending codes should be in alphabetical order!'))
            #===================================================================
            # Validation code for Racks
            #===================================================================
            r_st = record.rack_starting_code or ''
            r_end = record.rack_ending_code or ''
            
            if record.rack_code_type=='int':
                if not (r_st.isdigit() and r_end.isdigit()):
                    raise osv.except_osv(_('Warning'), _('Both Rack starting and ending code should be Numeric!'))
                if int(r_st) >= int(r_end):
                    raise osv.except_osv(_('Warning'), _('Rack starting code should be less than ending code!'))
                if int(record.rack_no_digits) == 2 and (int(r_st)>99 or int(r_end)>99) or (int(r_st)<0 or int(r_end)<0):
                    raise osv.except_osv(_('Warning'), _('Both Rack starting and ending code should be in range of 0 to 99!'))
                if int(record.rack_no_digits) == 1 and (int(r_st)>9 or int(r_end)>9) or (int(r_st)<0 or int(r_end)<0):
                    raise osv.except_osv(_('Warning'), _('Both Rack starting and ending code should be in range of 0 to 9!'))
            else:
                if int(record.rack_no_digits) == 1:
                    if not(r_st.upper() in alpha_codes and r_end.upper() in alpha_codes):
                        raise osv.except_osv(_('Warning'), _('Both Rack starting and ending code should be between A to Z!'))
                    
                    r_st_no = alpha_codes.index(r_st.upper())
                    r_end_no = alpha_codes.index(r_end.upper())
                    
                    if r_end_no <= r_st_no:
                        raise osv.except_osv(_('Warning'), _('Rack starting and Ending codes should be in alphabetical order!'))
                else:
                    r_st = len(r_st) == 2 and r_st or '-'+ r_st
                    r_end = len(r_end) == 2 and r_end or '-'+ r_end
                    if not(r_st.upper() in twoLetterSequence and r_end.upper() in twoLetterSequence):
                        raise osv.except_osv(_('Warning'), _('Both Rack starting and ending code should be between AA to ZZ!'))
                    
                    r_st_no = twoLetterSequence.index(r_st.upper())
                    r_end_no = twoLetterSequence.index(r_end.upper())
                    
                    if r_end_no <= r_st_no:
                        raise osv.except_osv(_('Warning'), _('Rack starting and Ending codes should be in alphabetical order!'))
            #===================================================================
            # Validation code for Shelfs
            #===================================================================
            s_st = record.shelf_starting_code or ''
            s_end = record.shelf_ending_code or ''
            
            if record.shelf_code_type=='int':
                if not (s_st.isdigit() and s_end.isdigit()):
                    raise osv.except_osv(_('Warning'), _('Both shelf starting and ending code should be Numeric!'))
                if int(s_st) >= int(s_end):
                    raise osv.except_osv(_('Warning'), _('Shelf starting code should be less than ending code!'))
                if int(record.shelf_no_digits) == 2 and (int(s_st)>99 or int(s_end)>99) or (int(s_st)<0 or int(s_end)<0):
                    raise osv.except_osv(_('Warning'), _('Both Shelf starting and ending code should be in range of 0 to 99!'))
                if int(record.shelf_no_digits) == 1 and (int(s_st)>9 or int(s_end)>9) or (int(s_st)<0 or int(s_end)<0):
                    raise osv.except_osv(_('Warning'), _('Both Shelf starting and ending code should be in range of 0 to 9!'))
            else:
                if int(record.shelf_no_digits) == 1:
                    if not(s_st.upper() in alpha_codes and s_end.upper() in alpha_codes):
                        raise osv.except_osv(_('Warning'), _('Both Shelf starting and ending code should be between A to Z!'))
                    
                    s_st_no = alpha_codes.index(s_st.upper())
                    s_end_no = alpha_codes.index(s_end.upper())
                    
                    if s_end_no <= s_st_no:
                        raise osv.except_osv(_('Warning'), _('Shelf starting and Ending codes should be in alphabetical order!'))
                else:
                    s_st = len(s_st) == 2 and s_st or '-'+ s_st
                    s_end = len(s_end) == 2 and s_end or '-'+ s_end
                    if not(s_st.upper() in twoLetterSequence and s_end.upper() in twoLetterSequence):
                        raise osv.except_osv(_('Warning'), _('Both Shelf starting and ending code should be between AA to ZZ!'))
                    
                    s_st_no = twoLetterSequence.index(s_st.upper())
                    s_end_no = twoLetterSequence.index(s_end.upper())
                    
                    if s_end_no <= s_st_no:
                        raise osv.except_osv(_('Warning'), _('Shelf starting and Ending codes should be in alphabetical order!'))
        return True

    _constraints = [
        (_check_codes, 'You cannot insert wrong codes format.',
            ['aisle_code_type','rack_code_type', 'shelf_code_type']),
        ]

    def button_confitm_locations(self,cr, uid, ids, context={}):
        for gen in self.browse(cr, uid, ids, context):
            gen.write({'state':'confirm'})
        return True
    
    def button_reset_draft(self,cr, uid, ids, context={}):
        for gen in self.browse(cr, uid, ids, context):
            gen.write({'state':'draft'})
        return True
    
    def unlink(self, cr, uid, ids, context=None):
        for gen in self.browse(cr, uid, ids, context=context):
            if gen.state !=  'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete a location generate record which is not in draft state!'))
        return super(locations_generator, self).unlink(cr, uid, ids, context)
    
    def button_generate_locations(self,cr, uid, ids, context={}):
        locations = self.button_preview_locations(cr,uid,ids,context)
        if locations:
            loc_pool = self.pool.get('stock.location')
            for gen in self.browse(cr, uid, ids, context):
                parent_loc = gen.parent_location.id
                for loc_name in locations:
                    if gen.skip:
                        exist = loc_pool.search(cr,uid,[('name','=',loc_name)])
                        if exist: continue
                        
                    loc_id = loc_pool.create(cr,uid,{'name':loc_name,'location_id':parent_loc,'gen_id':gen.id})
                gen.write({'state':'done'})
        return True

    def button_preview_locations(self,cr, uid, ids, context={}):
        alpha_codes = list(string.uppercase)
        twoLetterSequence  = ['-'+l for l in string.uppercase] + [ "%c%c" % (x, y) for x in range(ord('A'), ord('Z')+1) for y in range(ord('A'), ord('Z')+1)]
        for gen in self.browse(cr, uid, ids, context):
            locations = []
            if gen.aisle_code_type == 'char':
                ac = gen.aisle_starting_code
                ae = gen.aisle_ending_code
                
                if int(gen.aisle_no_digits) == 2:
                    ac = len(ac) == 2 and ac or '-'+ ac
                    ae = len(ae) == 2 and ae or '-'+ ae
                    a_start = twoLetterSequence.index(ac.upper())
                    a_end = twoLetterSequence.index(ae.upper())
                else:
                    a_start = alpha_codes.index(ac.upper())
                    a_end = alpha_codes.index(ae.upper())
            else:
                a_start = int(gen.aisle_starting_code)
                a_end = int(gen.aisle_ending_code)
            for asl in range(a_start, a_end+1):
                if int(gen.aisle_no_digits) == 1:
                    aisle = gen.aisle_code_type == 'char' and (alpha_codes[asl]) or ('%%0%sd' % gen.aisle_no_digits%asl)
                else:
                    aisle = gen.aisle_code_type == 'char' and (twoLetterSequence[asl]) or ('%%0%sd' % gen.aisle_no_digits%asl)
                if gen.rack_code_type == 'char':
                    rc = gen.rack_starting_code
                    re = gen.rack_ending_code
                    if int(gen.rack_no_digits) == 2:
                        rc = len(rc) == 2 and rc or '-'+ rc
                        re = len(re) == 2 and re or '-'+ re
                        r_start = twoLetterSequence.index(rc.upper())
                        r_end = twoLetterSequence.index(re.upper())
                    else:
                        r_start = alpha_codes.index(rc.upper())
                        r_end = alpha_codes.index(re.upper())
                else:
                    r_start = int(gen.rack_starting_code)
                    r_end = int(gen.rack_ending_code)
                for rc in range(r_start, r_end+1):
                    if int(gen.rack_no_digits) == 1:
                        rack = gen.rack_code_type == 'char' and (alpha_codes[rc]) or ('%%0%sd' % gen.rack_no_digits%rc)
                    else:
                        rack = gen.rack_code_type == 'char' and (twoLetterSequence[rc]) or ('%%0%sd' % gen.rack_no_digits%rc)
                    if gen.shelf_code_type == 'char':
                        sc = gen.shelf_starting_code
                        se = gen.shelf_ending_code
                        if int(gen.shelf_no_digits) == 2:
                            sc = len(sc) == 2 and sc or '-'+ sc
                            se = len(se) == 2 and se or '-'+ se
                            s_start = twoLetterSequence.index(sc.upper())
                            s_end = twoLetterSequence.index(se.upper())
                        else:
                            s_start = alpha_codes.index(sc.upper())
                            s_end = alpha_codes.index(se.upper())
                    else:
                        s_start = int(gen.shelf_starting_code)
                        s_end = int(gen.shelf_ending_code)
                    for slf in range(s_start, s_end+1):
                        if int(gen.shelf_no_digits) == 1:
                            shelf = gen.shelf_code_type == 'char' and (alpha_codes[slf]) or ('%%0%sd' % gen.shelf_no_digits%slf)
                        else:
                            shelf = gen.shelf_code_type == 'char' and (twoLetterSequence[slf]) or ('%%0%sd' % gen.shelf_no_digits%slf)
                        loc = str(aisle) +  str(rack) + str(shelf)
                        locations.append(loc)
                        
            temp_locs = ', '.join(locations)
            self.write(cr,uid,gen.id,{'temp_locs':temp_locs})
        return locations
locations_generator()  

class stock_location(osv.osv):
    
    _inherit = "stock.location"

    _columns = {
                'gen_id' : fields.many2one('locations.generator')
                }