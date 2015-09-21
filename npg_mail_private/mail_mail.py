# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 OpenERP S.A (<http://www.openerp.com>).
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

from openerp import SUPERUSER_ID
from openerp.osv import osv
from openerp.osv.orm import except_orm
from openerp.tools import append_content_to_html
from openerp.tools.translate import _
from openerp.osv import fields


class mail_mail(osv.Model):
    """ Update of mail_mail class, to add the signin URL to notifications. """
    _inherit = 'mail.mail'

    def send_get_mail_body(self, cr, uid, mail, partner=None, context=None):
        """ add a signin link inside the body of a mail.mail
            :param mail: mail.mail browse_record
            :param partner: browse_record of the specific recipient partner
            :return: the resulting body_html
        """
        partner_obj = self.pool.get('res.partner')
        model_obj = self.pool.get('ir.model')
        body = mail.body_html
        if partner:
            contex_signup = dict(context or {}, signup_valid=True)
            partner = partner_obj.browse(cr, SUPERUSER_ID, partner.id, context=contex_signup)
         
            model_id = model_obj.search(cr,uid,[('model','=', mail.model),], context=context)
            model = model_obj.browse(cr, SUPERUSER_ID, model_id[0], context=context)
            if model.name:    
                model_name = ('%s Document') % model.name 
            else:
                model_name = "OpenERP Document"
             
             # partner is an user and if has read acces:  change text to a link to the document s
            if partner.user_ids and mail.model and mail.res_id \
                    and self.check_access_rights(cr, partner.user_ids[0].id, 'read', raise_exception=False):

                related_user = partner.user_ids[0]
                try:
                    self.pool.get(mail.model).check_access_rule(cr, related_user.id, [mail.res_id], 'read', context=context)
                    url = partner_obj._get_signup_url_for_action(cr, uid, [partner.id], action='', res_id=mail.res_id, model=mail.model, context=context)[partner.id]
                    text = _("""<p> <a href="%s">Access the %s directly</a></p>""") % (url, model_name)
                except except_orm, e:
                    text = _("""<p>You have a new message for %s but you must contact the administrator for document access <a href="%s">View Message in Openerp Portal </a></p>""") % ( model_name, partner.signup_url )            

                    pass
            else:
                text = _("""<p> <a href="%s">Access messages and personal documents though our OpenERP Portal </a></p>""") % ( model_name, partner.signup_url )            
           
            body = append_content_to_html(("<div><p>%s</p></div>" % text),body, plaintext=False)
        return body
    
    
class mail_compose_message(osv.Model):
    _inherit = 'mail.compose.message'
    
    _columns = {
                'private_message' : fields.boolean("Private message", help="Send mail only to selected users and not to all followers of the document")
                }

    def send_mail(self, cr, uid, ids, context=None):
        context = context or {}
        if context.get('default_model') == 'sale.order' and context.get('default_res_id') and context.get('mark_so_as_sent'):
            context = dict(context, mail_post_autofollow=True)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'sale.order', context['default_res_id'], 'quotation_sent', cr)
        context.update({'private_message' : self.browse(cr, uid, ids[0], context=context).private_message})
        return super(mail_compose_message, self).send_mail(cr, uid, ids, context=context)

class mail_message(osv.Model):
    _inherit = 'mail.message'
    
    _columns = {
                'private_message' : fields.boolean("Private message", help="Send mail only to selected users and not to all followers of the document")
                }
    def _notify(self, cr, uid, newid, context=None):
        """ Add the related record followers to the destination partner_ids if is not a private message.
            Call mail_notification.notify to manage the email sending
        """
        notification_obj = self.pool.get('mail.notification')
        message = self.browse(cr, uid, newid, context=context)

        partners_to_notify = set([])
        # message has no subtype_id: pure log message -> no partners, no one notified
        if not message.subtype_id:
            return True

        # all followers of the mail.message document have to be added as partners and notified
        if message.model and message.res_id:
            fol_obj = self.pool.get("mail.followers")
            # browse as SUPERUSER because rules could restrict the search results
            fol_ids = []
            if not context.get('private_message'):
                fol_ids = fol_obj.search(cr, SUPERUSER_ID, [
                    ('res_model', '=', message.model),
                    ('res_id', '=', message.res_id),
                    ], context=context)
            partners_to_notify |= set(
                fo.partner_id for fo in fol_obj.browse(cr, SUPERUSER_ID, fol_ids, context=context)
                if message.subtype_id.id in [st.id for st in fo.subtype_ids]
            )
        # remove me from notified partners, unless the message is written on my own wall
        if message.author_id and message.model == "res.partner" and message.res_id == message.author_id.id:
            partners_to_notify |= set([message.author_id])
        elif message.author_id:
            partners_to_notify -= set([message.author_id])

        # all partner_ids of the mail.message have to be notified regardless of the above (even the author if explicitly added!)
        if message.partner_ids:
            partners_to_notify |= set(message.partner_ids)

        # notify
        if partners_to_notify:
            notification_obj._notify(cr, uid, newid, partners_to_notify=[p.id for p in partners_to_notify], context=context)
        message.refresh()

        # An error appear when a user receive a notification without notifying
        # the parent message -> add a read notification for the parent
        if message.parent_id:
            # all notified_partner_ids of the mail.message have to be notified for the parented messages
            partners_to_parent_notify = set(message.notified_partner_ids).difference(message.parent_id.notified_partner_ids)
            for partner in partners_to_parent_notify:
                notification_obj.create(cr, uid, {
                        'message_id': message.parent_id.id,
                        'partner_id': partner.id,
                        'read': True,
                    }, context=context)