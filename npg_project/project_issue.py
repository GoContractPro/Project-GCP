# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools

class project_issue(osv.osv):
    
    _inherit = "project.issue"
    
    _columns = {
                'logged_by_id': fields.many2one('res.users', 'Created By', required=False, select=1,
                         track_visibility='onchange'),
                'project_id': fields.many2one('project.project', 'Project', 
                        track_visibility='onchange', select=True,required=True ),
       
                }
    
    def _get_partner_contact(self, cr, uid, context=None):
        
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user and user.partner_id:
            return user.partner_id.id
        return super(project_issue, self)._get_partner_contact(cr, uid, context=context)

    def on_change_project2(self, cr, uid, ids, project_id, context=None):
        if project_id:
            project = self.pool.get('project.project').browse(cr, uid, project_id, context=context)
            if project and project.manager_id:
                return {'value': {'user_id': project.manager_id.id}}
        return {}
    
    _defaults = {
                 'user_id': False,
                 'logged_by_id' :lambda obj, cr, uid, context: uid,
                 'partner_id': lambda s, cr, uid, c: s._get_partner_contact(cr, uid, c),
                 }
    
class project_project(osv.osv):
    
    _inherit = 'project.project'
    
    _columns ={
               'manager_id': fields.many2one('res.users', 'Project Manager',
                    help="""Project manager or lead contact on team. \
                            Will be the default assigned to on Issues"""),
               }

class res_users(osv.osv):
    
    _inherit = 'res.users'
    
    
    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
            
        if context.get('search_project_members', False):
            
            project = self.pool.get('project.project').browse(cr,uid,context.get('search_project_members'),context=context)
             
            if project and project.members:
                
                members = [i.id for i in project.members]  
                 
                args += [('id', 'in', members)]
        
                ids = []
                
                positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']

                if operator in positive_operators:
                    ids = self.search(cr, uid, [('name',operator,name)]+ args, limit=limit, context=context)
                else:
                    ids = self.search(cr, uid, args, limit=limit, context=context)
                result = self.name_get(cr, uid, ids, context=context) 
                return result  

        return super(res_users, self).name_search(cr, uid, name, args, operator,context, limit=limit)

        
        
res_users()
    



    