# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group INC (<http://www.novapointgroup.com>)
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

{
    'name': 'Odoo link Top of Mail',
    'version': '1.0',
    'category': '',
    "sequence": 14,
    'complexity': "easy",
    'category': 'Generic Modules/Others',
    'description': """
       
     Enhancement to mail moves  Document links to top of email mailer from standard location after
     Signature. This give link more visibility when viewed on Emails  and avoids links hidden by folding 
     Signature area on email.
      
    """,
    'author': 'NovaPoint Group Inc, Stephen  Levenhagen',
    'website': 'www.novapointgroup.com',
    'depends': ["base","mail"],
    'init_xml': [],
    'data': [],
    'demo_xml': [],
    'test': [],
    'qweb' : [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
