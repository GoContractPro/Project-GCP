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

from osv import fields, osv
import time
import sys 
sys.setrecursionlimit(10000)

from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP


class srs_software_package(osv.osv):
    _name = "srs.software.package"
    _columns = {
     'name':fields.char('Version',size=64),
     'repository':fields.char('Repository',size=64),
     'author':fields.char('Author',size=64),
     'website':fields.char('Website',size=64),
       }

srs_software_package()

class srs_use_case(osv.osv):
    _name = "srs.use.case"
    _columns = {
     'name':fields.char('ID',size=64,readonly=True),
     'sequence': fields.integer('Sequence'),
     'desc':fields.text('Description'),
     'case_ids': fields.one2many('srs.use.case.line', 'ucase_id', 'Attributes'),
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            seq = self.pool.get('ir.sequence').get(cr, uid,'srs.use.case') or '/'
            vals['name']=seq
        return super(srs_use_case, self).create(cr, uid, vals, context=context)
    
    _defaults = {        
        'name': lambda obj, cr, uid, context: '/', 
       }

srs_use_case()

class srs_use_case_line(osv.osv):
    _name = "srs.use.case.line"
    _columns = {
     'name':fields.char('ID',size=64),
     'sequence': fields.integer('Sequence'),
     'desc':fields.text('Description'),
     'expt_result':fields.text('Expected Results'),
     'ucase_id': fields.many2one('srs.use.case','Use Case'),
    }

srs_use_case_line()

class srs_user_guide(osv.osv):
    _name = "srs.user.guide"
    _columns = {
     'name':fields.char('Name',size=64),
     'sequence': fields.integer('Sequence'),
     'guide_ids': fields.one2many('srs.user.guide.line', 'gcase_id', 'User Guide Line'),
    }
srs_user_guide()

class srs_user_guide_line(osv.osv):
    _name = "srs.user.guide.line"
    _columns = {
     'name':fields.char('Version',size=64),
     'author': fields.integer('Author'),
     'desc':fields.text('Description'),
     'input_file': fields.binary('Attachment'),
     'fname': fields.char('Name', size=64), 
     'soft_pack_id': fields.many2one('srs.software.package','Software Package'),
     'gcase_id': fields.many2one('srs.user.guide','SRS User Guide'),
    }

srs_user_guide_line()

class srs(osv.osv):
    _name = "srs"
    _columns = {
     'name':fields.char('ID',size=64,readonly=True),
     'parent_id':fields.many2one('srs','Parent'),
     'sequence': fields.integer('Sequence'),
     'desc':fields.text('Requirements'),
     'time':fields.float('Estimate Time'),
     'srs_package_ids': fields.many2many('srs.software.package', 'rel_srs_soft_package', 'soft_pack_srs', 'soft_pack_id', 'Related Software'),
     'srs_use_case_ids': fields.many2many('srs.use.case', 'rel_software_use_case', 'use_case_software', 'srs_use_id', 'Related Use Cases'),
     'srs_user_guides': fields.many2many('srs.user.guide', 'rel_srs_user_guide', 'user_guide_srs', 'guide_srs_id', 'Related User Guides'),
       }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            seq = self.pool.get('ir.sequence').get(cr, uid,'srs') or '/'
            vals['name']=seq
        return super(srs, self).create(cr, uid, vals, context=context)
    
    _defaults = {        
           'name': lambda obj, cr, uid, context: '/', 
      }

srs()



