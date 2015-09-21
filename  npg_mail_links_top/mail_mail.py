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
    
    