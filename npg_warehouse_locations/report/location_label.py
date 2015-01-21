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
from openerp import pooler
import time
from openerp.report import report_sxw

class location_label(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(location_label, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'process':self.process,
        })
        
    def process(self, location_id):
        location_obj = pooler.get_pool(self.cr.dbname).get('stock.location')
        data = location_obj._product_get_all_report(self.cr,self.uid, [location_id])
        data['location_name'] = location_obj.read(self.cr, self.uid, [location_id],['complete_name'])[0]['complete_name']
        return [data]

report_sxw.report_sxw('report.location_label', 'stock.location', 'addons/npg_warehouse_locations/report/location_label.rml', parser=location_label,header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

