from base_status.base_stage import base_stage
import crm
from osv import fields, osv
from tools.translate import _
from tools import html2plaintext
from base.res.res_partner import format_address
from datetime import datetime, timedelta
import time
import smtplib
from validate_email import validate_email
from openerp import tools


class email_status(osv.osv):
    _name = "email.status"
    _columns = {
                'marketing_workitem_id':fields.many2one('marketing.campaign.workitem',"Marketing Workitem"),
                'partner_id':fields.many2one('res.partner'),
                'email_opened':fields.boolean('Email Opened'),
                'date_time':fields.datetime("Open Time"),
                'date_open' : fields.datetime("Email Open Time"),
                }
email_status()
    
class website_visit_status(osv.osv):
    _name = "website.visit.status"
    _columns = {
                'marketing_workitem_id':fields.many2one('marketing.campaign.workitem',"Marketing Workitem"),
                'partner_id':fields.many2one('res.partner'),
                'website_visit':fields.boolean('Website Visited'),
                'date_time':fields.datetime("Open Time"),
                'date_visit' : fields.datetime("Visit Time"),
                }
    
website_visit_status()

class res_partner(osv.osv):
    
    _name = 'res.partner'
    _inherit='res.partner'
    _columns={
              'inv_email':fields.char('Invalid Email',size=64),
              'stamp_time':fields.char('Stamp Time',size=64),
#               'email_valid': fields.function(_get_valid_mail, method=True, store=True, type='boolean',string='Invalid Email'),
              'email_invalid': fields.boolean("Invalid Email"),
              'email_status' : fields.one2many('email.status','partner_id', "Email Status"),
              'website_visit_status' : fields.one2many('website.visit.status','partner_id', "Website Visited"),
              }
    
    def get_valid_mail(self, cr, uid, ids, context=None):
        email_valid = False
        for part in self.browse(cr,uid,ids,context):
            email_valid =validate_email(part.email or '',verify=True,debug=True)
            part.write({'email_invalid':not email_valid})
        return email_valid
    
    def unsubscribe_mail(self,cr,uid,args=None,context=None):
        if args is None:
            args = {}
        if context is None:
            context = {}
    
        if args.get('partner_id'):
            self.write(cr,uid,[args.get('partner_id')],{'opt_out':True}, context)
            return True
        if args.get('email'):
            cr.execute('update res_partner set opt_out=%s where email=%s',(True,args.get('email')))
            return True
        else:
            return False
    
    def check_mail(self,cr,uid,ids,context=None):
        for val in self.browse(cr,uid,ids,context=None):
            if val.email:   
                self.unsubscribe_mail(cr,uid,val.email,context)
        return True
    
    def update_email_status(self,cr,uid,partner_id = False, workitem_id=False):
        res = 'Partner not found'
        if partner_id:
            self.pool.get('email.status').create(cr,uid,{'partner_id':partner_id,'marketing_workitem_id':workitem_id, 'email_opened':True,'date_open':time.strftime('%Y-%m-%d %H:%M:%S')})
            res = "Record updated"
        return res
    
    def update_website_visit_status(self,cr,uid,partner_id = False, workitem_id=False):
        res = 'Partner not found'
        if partner_id:
            self.pool.get('website.visit.status').create(cr,uid,{'partner_id':partner_id,'marketing_workitem_id':workitem_id, 'website_visit':True,'date_visit':time.strftime('%Y-%m-%d %H:%M:%S')})
            res = "Record updated"
        return res

res_partner()

class marketing_campaign_workitem(osv.osv):
    _inherit = "marketing.campaign.workitem"
    
    _columns = {
              'email_status' : fields.one2many('email.status','marketing_workitem_id', "Email Status"),
              'website_visit_status' : fields.one2many('website.visit.status','marketing_workitem_id', "Website Visited"),
              }
    
    def update_campain_click_status(self,cr,uid,args = None , context = None):
 # TODO add code  here to update click time Stamps from PHP will search base on 
 # agruments passed for partner_id and 'activity_id.name'       
        return True
    
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['campaign_id','activity_id'], context=context)
        res = []
        for record in reads:
            name = str(record['id'])
            if record['campaign_id']:
                name = '[' + name + ']' + record['campaign_id'][1]
            if record['activity_id']:
                name = name + '--' +record['activity_id'][1]
                
            res.append((record['id'], name))
        return res
    
class marketing_campaign_activity(osv.osv):
    _inherit = "marketing.campaign.activity"
    
    def _process_wi_email(self, cr, uid, activity, workitem, context=None):
        if context is None:
            context = {}
        context.update({'workitem_id':workitem.id})
        return self.pool.get('email.template').send_mail(cr, uid,
                                            activity.email_template_id.id,
                                            workitem.res_id, context=context)
 


class email_template(osv.osv):
    "Templates for sending email"
    _inherit = "email.template"
    
    _columns = {
                'header_html': fields.text('Header', translate=True, help="Rich-text/HTML for header Part of mail body"),
                'footer_html': fields.text('Footer', translate=True, help="Rich-text/HTML for Footer Part of mail body"),
                }

    #===========================================================================
    # def generate_email(self, cr, uid, template_id, res_id, context=None):
    #     if context is None:
    #         context = {}
    #     values = super(email_template, self).generate_email(cr, uid, template_id, res_id, context=context)
    #     workitem_id = context.get('workitem_id')
    #     if workitem_id:
    #         work_item = "Work Item : " + str(workitem_id)
    #         values['body_html'] = tools.append_content_to_html(values['body_html'], work_item)
    #     return values
    #===========================================================================
    
    """ 
    def send_mail(self, cr, uid, template_id, res_id, force_send=False, context=None):
        part = 'res.partner'
        partner_obj = self.pool.get(part)
        email_valid = True
        template = self.get_email_template(cr, uid, template_id, res_id, context)
        if template.model == part:
            email_valid = partner_obj.get_valid_mail(cr,uid,[res_id])
        if not email_valid:
            raise osv.except_osv(_('Warning!'),_("To Email address is not valid"))
        return super(email_template, self).send_mail(cr, uid, template_id, res_id, force_send, context)
    """
    def generate_email(self, cr, uid, template_id, res_id, context=None):
        """Generates an email from the template for given (model, res_id) pair.

           :param template_id: id of the template to render.
           :param res_id: id of the record to use for rendering the template (model
                          is taken from template definition)
           :returns: a dict containing all relevant fields for creating a new
                     mail.mail entry, with one extra key ``attachments``, in the
                     format [(report_name, data)] where data is base64 encoded.
        """
        if context is None:
            context = {}
        report_xml_pool = self.pool.get('ir.actions.report.xml')
        template = self.get_email_template(cr, uid, template_id, res_id, context)
        ctx = context.copy()
        if template.lang:
            ctx['lang'] = template._context.get('lang')
        values = {}
        
        for field in ['subject', 'body_html', 'email_from',
                      'email_to', 'email_recipients', 'email_cc', 'reply_to']:
            values[field] = self.render_template(cr, uid, getattr(template, field),
                                                 template.model, res_id, context=ctx) \
                                                 or False
        for field in ['header_html', 'footer_html',]:
#            if context.get('workitem_id'):
                values[field] = self.render_template(cr, uid, getattr(template, field),
                                                 'marketing.campaign.workitem', context.get('workitem_id'), context=ctx) \
                                                 or False                                                 
                                                 
        if values['header_html']:
#             values['body_html'] = tools.append_content_to_html( values['header_html'],values['body_html'])
            values['body_html'] = values['header_html'] + "\n" + values['body_html']
            del values['header_html']
        if template.user_signature:
            signature = self.pool.get('res.users').browse(cr, uid, uid, context).signature
            if signature:
                values['body_html'] = tools.append_content_to_html(values['body_html'], signature)
                
        if values['footer_html']:
#             values['body_html'] = tools.append_content_to_html(values['body_html'], values['footer_html'])
            values['body_html'] = values['body_html'] + "\n" + values['footer_html']
            del values['footer_html']
  #      workitem_id = context.get('workitem_id')
  #      if workitem_id:
  #          work_item = "Work Item : " + str(workitem_id)
  #          values['body_html'] = tools.append_content_to_html(values['body_html'], work_item)
            
            
        if values['body_html']:
            values['body'] = tools.html_sanitize(values['body_html'])

        values.update(mail_server_id=template.mail_server_id.id or False,
                      auto_delete=template.auto_delete,
                      model=template.model,
                      res_id=res_id or False)
        print values['body_html']
        attachments = []
        # Add report in attachments
        if template.report_template:
            report_name = self.render_template(cr, uid, template.report_name, template.model, res_id, context=ctx)
            report_service = 'report.' + report_xml_pool.browse(cr, uid, template.report_template.id, context).report_name
            # Ensure report is rendered using template's language
            service = netsvc.LocalService(report_service)
            (result, format) = service.create(cr, uid, [res_id], {'model': template.model}, ctx)
            # TODO in trunk, change return format to binary to match message_post expected format
            result = base64.b64encode(result)
            if not report_name:
                report_name = report_service
            ext = "." + format
            if not report_name.endswith(ext):
                report_name += ext
            attachments.append((report_name, result))

        attachment_ids = []
        # Add template attachments
        for attach in template.attachment_ids:
            attachment_ids.append(attach.id)

        values['attachments'] = attachments
        values['attachment_ids'] = attachment_ids
        return values