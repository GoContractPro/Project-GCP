# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
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

{
    "name" : "Import Open Invoices and Credit Memos",
    "version" : "1.0",
    "author" : 'Novapoint Group LLC',
    "description": """This module provides the ability to import open (customer and supplier) invoices/credit memos into
OpenERP from a previous ERP system. It will also allow the imported invoices/
credit memo to bypass the normal DRAFT to OPEN workflow behavior and use special
routing based on indicators when imported. After the open invoices/credit memos are
loaded into OpenERP, the behavior and available functions will be the same as an invoice/
credit memo which originated in OpenERP. i.e. processing of payments, cancellations,
refunds, inventory tracking and the like.

The goal is to be able to bring in the “full detail” of invoices and credit memos typically
found in invoices opened in OpenERP including:
• Partner names
• Addresses (Invoice, shipping, contact)
• Existing invoice number (created in another system) ← OpenERP doesn’t assign a
new invoice
• Payment Terms
• Invoice Date
• Invoice line items
• Invoice taxes (if applicable)
• Invoice totals (if applicable)
• Shipping Method (if applicable)
• And additional fields as necessary and required

And new fields including:
• Opening Balance Invoice – boolean field
• Opening Balance Journals which may be user defined journals such as:

    1) Open Customer Invoice
    2) Open Supplier Invoice
    3) Open Customer Credit Memo
    4) Open Supplier Credit Memo

""",
    "category" : "Generic Modules/Accounting",
    "website" : "http://www.novapointgroup.com/",
    "depends" : ["account",'account_cancel'],
    "init_xml" : [],
    "demo_xml" : [ "account_journal_data.xml"],
    "update_xml" : [
    "account_invoice_view.xml",
    "account_invoice_workflow.xml"
    ],
    "test" : [],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

