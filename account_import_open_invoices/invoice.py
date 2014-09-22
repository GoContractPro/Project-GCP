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
import time

import netsvc
from osv import fields, osv
from tools.translate import _

class account_invoice(osv.osv):

    _name = "account.invoice"
    _description = 'Invoice'
    _inherit = 'account.invoice'
    _columns = {
        'internal_number': fields.char('Invoice Number', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Unique number of the invoice assigned with the import of open invoices."),
        'special_journal_id': fields.many2one('account.journal', 'Special Journal', readonly=True, states={'draft':[('readonly',False)]}),
        'open_invoice': fields.boolean('Open Invoice', readonly=True, states={'draft':[('readonly',False)]}, help="Indicates it is an open invoice/memo"),
    }

    def action_move_create_special(self, cr, uid, ids, context=None):
        """
        Creates journal entries for open invoices.
        Duplicated code from action_move_create() with modifications such as:
            a) Move is posted on the Special journal
            instead of the invoice journal.
            b) Move line is created for the off balance sheet account of the special journal
            instead of the Product Sales Income/Expense accounts.
        """

        if context is None:
            context = {}

        ait_pool = self.pool.get('account.invoice.tax')
        currency_pool = self.pool.get('res.currency')
        sequence_pool = self.pool.get('ir.sequence')
        period_pool = self.pool.get('account.period')
        move_pool = self.pool.get('account.move')

        for inv in self.browse(cr, uid, ids):
            period = False
            company_currency = inv.company_id.currency_id.id
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines !'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            # Constraints for 'open' invoices.
            if not inv.special_journal_id:
                raise osv.except_osv(_('No Special Journal !'),
                        _("The 'open' invoice must have special journal"))
            journal = self.pool.get('account.journal').browse(cr, uid, inv.special_journal_id.id)
            if not journal.default_credit_account_id or not journal.default_debit_account_id:
                raise osv.except_osv(_('No default debit and credit account in special journal !'),
                    _('The journal must have default credit and debit account'))
            if journal.centralisation:
                raise osv.except_osv(_('UserError'),
                        _('Cannot create invoice move on centralised journal'))

            if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0):
                print id, inv.id		
                raise osv.except_osv(_('Bad total !'), _('Please verify the price of the invoice !\nThe real total does not match the computed total.'))

            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': time.strftime('%Y-%m-%d')})
            # Create the analytical lines:
            # one move line per invoice line.
            iml = self._get_analytic_lines(cr, uid, inv.id)
            # Check if taxes are all computed.
            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            compute_taxes = ait_pool.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_pool)

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise osv.except_osv(_('Error !'), _("Cannot create the invoice !\nThe payment term defined gives a computed amount greater than the total invoiced amount."))

            # Create one move line per tax line.
            iml += ait_pool.move_line_get(cr, uid, inv.id)

            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = self._convert_ref(cr, uid, inv.number)
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'

            diff_currency_p = inv.currency_id.id <> company_currency
            # Create one move line for the total and possibly adjust the other lines amount.
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml)

            # Empty the list since we don't want to generate move line for Product Sales Income/Expense Account.
            iml = []

            acc_id = inv.account_id.id
            totlines = False
            if inv.payment_term:
                totlines = self.pool.get('account.payment.term').compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                # Create move line per payment term line.
                for t in totlines:
                    if inv.currency_id.id != company_currency:
                        amount_currency = currency_pool.compute(cr, uid,
                                company_currency, inv.currency_id.id, t[1])
                    else:
                        amount_currency = False
                    # Last line add the diff.
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': inv['name'] or '/',
                        'price': t[1],
                        'account_id': acc_id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency_p and  amount_currency or False,
                        'currency_id': diff_currency_p and inv.currency_id.id or False,
                        'ref': ref,
                    })
            else:
                # For single payment term line, create one move line for the total amount.
                iml.append({
                    'type': 'dest',
                    'name': inv['name'] or '/',
                    'price': total,
                    'account_id': acc_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p and total_currency or False,
                    'currency_id': diff_currency_p and inv.currency_id.id or False,
                    'ref': ref
            })

            # Create a move line for the off balance sheet account which would either be
            # the default debit account or the default credit account from the
            # special journal depending on the type of invoice
            iml.append({
                'type': 'src',
                'name': inv['name'] or '/',
                'price': -total,
                'account_id': total > 0 and journal.default_credit_account_id.id or
                                journal.default_debit_account_id.id,
                'amount_currency': diff_currency_p and total_currency or False,
                'currency_id': diff_currency_p and inv.currency_id.id or False,
                'ref': ref
            })

            line = map(lambda x:(0, 0, self.line_get_convert(cr, uid, x, inv.partner_id.id, inv.date_invoice, context=context)), iml)
            line = self.finalize_invoice_move_lines(cr, uid, inv, line)
            # Get the period from the invoice date and add
            # period_id in the move lines.
            period_id = inv.period_id and inv.period_id.id or False
            if not period_id:
                period_ids = period_pool.search(cr, uid, [('date_start','<=',inv.date_invoice or time.strftime('%Y-%m-%d')),
                                ('date_stop','>=',inv.date_invoice or time.strftime('%Y-%m-%d')),
                                ('company_id', '=', inv.company_id.id)])
                period_id = period_ids and period_ids[0]
            if period_id:
                period = period_pool.browse(cr, uid, period_id, context=context)
                for i in line:
                    i[2]['period_id'] = period_id
            # Have the same name for the move as the internal number in the imported csv file
            # otherwise use the sequence of the special journal.
            new_move_name = inv.internal_number or False
            if not new_move_name:
                if journal.sequence_id:
                    c = {'fiscalyear_id': period and period.fiscalyear_id.id or False}
                    new_move_name = sequence_pool.get_id(cr, uid, journal.sequence_id.id, context=c)
                else:
                    raise osv.except_osv(_('Error'), _('No sequence defined on the special journal !'))
            # Create a move for the special journal and
            # make the invoice point to that move.
            move = {
                'name': new_move_name,
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice or time.strftime('%Y-%m-%d'),
                'type': entry_type,
                'narration': inv.comment,
                'period_id': period_id
            }
            move_id = move_pool.create(cr, uid, move, context=context)
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id': period_id, 'move_name': new_move_name})

        self._log_event(cr, uid, ids)
        return True

    def action_cancel(self, cr, uid, ids, *args):
        """Prevents the canceling operation on open invoices whose journal entries are posted."""
        for invoice in self.browse(cr, uid, ids, *args):
            if invoice.open_invoice and \
                invoice.move_id and \
                invoice.move_id.state=='posted':
                # The user is not allowed to cancel an invoice with journal entries posted. However, he can refund an open invoice.
                # But on an open credit memo, he is not allowed to refund too.
                if invoice.type in ['in_invoice','out_invoice']:
                    err_msg = _('You cannot cancel an open invoice whose journal entry is posted!\nPlease issue a refund!')
                else:
                    err_msg = _('You cannot cancel an open credit memo whose journal entry is posted !')
                raise osv.except_osv(_('Error !'), err_msg)
        return super(account_invoice, self).action_cancel(cr, uid, ids, *args)


    def copy(self, cr, uid, id, default={}, context=None):
        default.update({
            'open_invoice': False,
            'special_journal_id': False,
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)

    def action_process(self, cr, uid, ids, context=None):
        """Prevents the refund operation on open credit memo."""
        if context is None:
            context = {}
        # Allow to refund if it is not an open credit memo.
        inv_pool = self.pool.get('account.invoice')
        for invoice in inv_pool.browse(cr, uid, ids, context=context):
            if invoice.open_invoice and invoice.type in ['out_refund', 'in_refund']:
                raise osv.except_osv(_('Error !'), _('You cannot refund an open credit memo!'))
        return {
            'name':_("Refund"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.invoice.refund',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': dict(context, active_ids=ids)
        }

account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:






















