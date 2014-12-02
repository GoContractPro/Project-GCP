from base_status.base_stage import base_stage
import crm
from osv import fields, osv
from tools.translate import _
from tools import html2plaintext
from base.res.res_partner import format_address
import datetime
import time


class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit='res.partner'
    
    def unsubscribe_mail(self,cr,uid,email,context):
         if email:
             cr.execute('update res_partner set opt_out=%s where email=%s',(True,email))
         return True
    
    def check_mail(self,cr,uid,ids,context=None):
        for val in self.browse(cr,uid,ids,context=None):
            if val.email:   
                self.unsubscribe_mail(cr,uid,val.email,context)
        return True

res_partner()
    

