from base_status.base_stage import base_stage
import crm
from osv import fields, osv
from tools.translate import _
from tools import html2plaintext
from base.res.res_partner import format_address
import datetime
import time
import smtplib
from validate_email import validate_email


class email_status(osv.osv):
    _name = "email.status"
    _columns = {
                'partner_id':fields.many2one('res.partner'),
                'email_opened':fields.boolean('Email Opened'),
                'date_time':fields.datetime("Open Time"),
                'date_open' : fields.char("Email Open Time",size=64),
                }
email_status()
    
class website_visit_status(osv.osv):
    _name = "website.visit.status"
    _columns = {
                'partner_id':fields.many2one('res.partner'),
                'website_visit':fields.boolean('Website Visited'),
                'date_time':fields.datetime("Open Time"),
                'date_visit' : fields.char("Visit Time",size=64),
                }
    
website_visit_status()

class res_partner(osv.osv):
    
    def _get_valid_mail(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for part in self.browse(cr,uid,ids):
            valid_email =validate_email(part.email or '',verify=True)
            if valid_email:
                result[part.id] =False
            else :
                result[part.id] =True
        return result
            
    _name = 'res.partner'
    _inherit='res.partner'
    _columns={
              'inv_email':fields.char('Invalid Email',size=64),
              'stamp_time':fields.char('Stamp Time',size=64),
              'email_valid': fields.function(_get_valid_mail, method=True, store=True, type='boolean',string='Invalid Email'),
              
              'email_status' : fields.one2many('email.status','partner_id', "Email Status"),
              'website_visit_status' : fields.one2many('website.visit.status','partner_id', "Website Visited"),
              }
    
    def unsubscribe_mail(self,cr,uid,email):
        if email:
            cr.execute('update res_partner set opt_out=%s where email=%s',(True,email))
            return True
        else:
            return False
    
    def check_mail(self,cr,uid,ids,context=None):
        for val in self.browse(cr,uid,ids,context=None):
            if val.email:   
                self.unsubscribe_mail(cr,uid,val.email,context)
        return True
    
    def update_email_status(self,cr,uid,email,opened,date_time=None):
        partner_id =[]
        res = 'Partner not found'
        if email:
            partner_id = self.search(cr,uid,[('email','=',email)])
        if partner_id:
            self.pool.get('email.status').create(cr,uid,{'partner_id':partner_id[0],'email_opened':opened,'date_open':date_time})
            res = "Record updated"
        return res

    def update_website_visit_status(self,cr,uid,email,visit,date_time=None):
        partner_id =[]
        res = 'Partner not found'
        if email:
            partner_id = self.search(cr,uid,[('email','=',email)])
        if partner_id:
            self.pool.get('website.visit.status').create(cr,uid,{'partner_id':partner_id[0],'website_visit':visit,'date_visit':date_time})
            res = "Record updated"
        return res

res_partner()

    