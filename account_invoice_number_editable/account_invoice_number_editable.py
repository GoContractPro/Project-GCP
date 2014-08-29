# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2014 Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
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

from openerp.osv import fields,osv
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

from openerp import pooler

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    # add sql constraints for the uniq internal number
    _columns = {
                'internal_number': fields.char('Invoice Number', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Unique number of the invoice, computed automatically when the invoice is created."),
    }
    _sql_constraints = [
        ('internal_number_uniq', 'unique(internal_number)', 'Please check the Invoice Number. The number already exists in the system!.'),
    ]
    
    def onchange_internal_number(self, cr, uid, ids, internal_number, context=None):
        if context is None:
            context = {}        
        if internal_number:
            inv_id = self.search(cr, uid, [('internal_number','=',internal_number)])
            if inv_id:
                raise osv.except_osv(_('Warning!'), _('Please check the Invoice Number. The number already exists in the system!.'))
            else:
                return {'value': {'internal_number': internal_number}}
        else:
            return {'value': {'internal_number': False}}

account_invoice()

