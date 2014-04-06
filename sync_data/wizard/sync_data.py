from osv import orm,fields

import xmlrpclib
import logging

_logger = logging.getLogger(__name__)

class sync_data(orm.TransientModel):
    
    _name = "sync.data"
    
    _description = "syncronous data"
    
    _columns = {
         'name' : fields.char('Server', size=32),
         'port' : fields.integer('Port'),
         'db_name' : fields.char('DB Name',size=32),
         'user_name' : fields.char('User Name',size=32),
         'password' : fields.char('Password',size=32)
                
    }
    
    _defaults = {
        'name' : 'localhost',
         'port' : 8601,
         'db_name' : 'npg6m',
         'user_name' : 'admin',
         'password' : 'P@ssw0rd'
    }
    
    
    def import_user(self, cr, uid, ids, context=None):
        """
        This method can imports 'UserData' from 6.0 to 7.0 AND Performs the 
        fields matching between these two files's data and model's columns.
        
        Returns common User fields's data..
        Add information into user form..
        """
        
        
        user_pool = self.pool.get('res.users')
        for rec in self.browse(cr, uid, ids, context=context):
            sock_comman = xmlrpclib.ServerProxy('http://' +rec.name + ':' + str(rec.port) +'/xmlrpc/common')
            user_id = sock_comman.login(rec.db_name, rec.user_name, rec.password)
            sock = xmlrpclib.ServerProxy('http://' +rec.name + ':' +str(rec.port) +'/xmlrpc/object', allow_none=True)
            user_ids = sock.execute(rec.db_name, user_id, rec.password, 'res.users', 'search', [('id', '!=', 1)])
            users = sock.execute(rec.db_name, user_id, rec.password, 'res.users', 'read', user_ids, [])
            for user in users:
                data = {}
                data['name'] = user.get('name')
                data['login'] = user.get('login')
                data['password'] = user.get('password')
                data['active'] = user.get('active')
                data['email'] = user.get('user_email')
                data['company_id'] = 1
                data['menu_id'] = 1
                data['notification_email_send'] = 'comment'
                user_pool.create(cr, uid , data, context=context)
        return True
    
    def import_partner(self, cr, uid, ids, context=None):
        """
        This method can imports 'CustomersData' from 6.0 to 7.0 AND Performs the 
        fields matching between these two files's data and model's columns.
        
        Returns common customers fields's data..
        Add information into customers form..
        """
        
        partner_pool = self.pool.get('res.partner')
        country_pool = self.pool.get('res.country')
        state_pool = self.pool.get('res.country.state')
        for rec in self.browse(cr, uid, ids, context=context):
            sock_comman = xmlrpclib.ServerProxy('http://' +rec.name + ':' + str(rec.port) +'/xmlrpc/common')
            user_id = sock_comman.login(rec.db_name, rec.user_name, rec.password)
            sock = xmlrpclib.ServerProxy('http://' +rec.name + ':' +str(rec.port) +'/xmlrpc/object', allow_none=True)
            partner_ids = sock.execute(rec.db_name, user_id, rec.password, 'res.partner', 'search', [])
            partners = sock.execute(rec.db_name, user_id, rec.password, 'res.partner', 'read', partner_ids, [])
            for partner in partners:
                 data = {}
                 data['name'] = partner.get('name')
                 data['customer'] = partner.get('customer')
                 data['supplier'] = partner.get('supplier')
                 data['website'] = partner.get('website')
                 data['property_account_position'] = partner.get('property_account_position')
                 data['credit_limit'] = partner.get('credit_limit')

                 address_ids = sock.execute(rec.db_name, user_id, rec.password, 'res.partner.address', 'search', [('partner_id','=',partner.get('id')),('type','=','default')])
                 addresses = sock.execute(rec.db_name, user_id, rec.password, 'res.partner.address', 'read', address_ids, [])
                 add_id = False
                 if addresses:
                     add_id = addresses[0].get('id')
                     data['city'] = addresses[0].get('city')
                     data['phone'] = addresses[0].get('phone')
                     data['mobile'] = addresses[0].get('mobile')
                     data['fax'] = addresses[0].get('fax')
                     data['email'] = addresses[0].get('email')
                     data['street'] = addresses[0].get('street')
                     data['street2'] = addresses[0].get('street2')
                     data['zip'] = addresses[0].get('zip')
                     if addresses[0].get('country_id', False):
                         country_ids = country_pool.search(cr, user_id, [('name','=', addresses[0]['country_id'][1])])
                         if country_ids:
                             data['country_id'] = country_ids[0]
                     if addresses[0].get('state_id', False):
                         state_ids = state_pool.search(cr, user_id, [('name','=', addresses[0]['state_id'][1])])
                         if state_ids:
                             data['state_id'] = state_ids[0]
                 partner_id = partner_pool.create(cr, uid , data, context=context)
                 if add_id:
                     other_address_ids = sock.execute(rec.db_name, user_id, rec.password, 'res.partner.address', 'search', [('partner_id','=',partner.get('id')),('id','!=',add_id)])
                     other_addresses = sock.execute(rec.db_name, user_id, rec.password, 'res.partner.address', 'read', other_address_ids, [])
                     if other_addresses:
                         partner_pool.write(cr, uid, [int(partner_id)], {'is_company' : True})
                     for address in other_addresses:
                         add_data = {}
                         add_data['name'] = address.get('name', '/')
                         add_data['city'] = address.get('city')
                         add_data['phone'] = address.get('phone')
                         add_data['mobile'] = address.get('mobile')
                         add_data['fax'] = address.get('fax')
                         add_data['email'] = address.get('email')
                         add_data['street'] = address.get('street')
                         add_data['street2'] = address.get('street2')
                         add_data['zip'] = address.get('zip')
                         add_data['parent_id'] = partner_id
                         if address.get('country_id', False):
                             country_ids = country_pool.search(cr, user_id, [('name','=', address['country_id'][1])])
                             if country_ids:
                                 add_data['country_id'] = country_ids[0]
                         if address.get('state_id', False):
                             state_ids = state_pool.search(cr, user_id, [('name','=', address['state_id'][1])])
                             if state_ids:
                                 add_data['state_id'] = state_ids[0]
                         partner_pool.create(cr, uid , add_data, context=context)
        return True
    
    def import_account(self, cr, uid, ids, context=None):
        """
        This method can imports 'Analytic Account Data' from 6.0 to 7.0 AND Performs the 
        fields matching between these two files's data and model's columns.
        
        Returns common account fields's data..
        Add information into analytic accounts form..
        """
        account_pool = self.pool.get('account.analytic.account')
        partner_pool = self.pool.get('res.partner')
        user_pool = self.pool.get('res.users')
        for rec in self.browse(cr, uid, ids, context=context):
            sock_comman = xmlrpclib.ServerProxy('http://' +rec.name + ':' + str(rec.port) +'/xmlrpc/common')
            user_id = sock_comman.login(rec.db_name, rec.user_name, rec.password)
            sock = xmlrpclib.ServerProxy('http://' +rec.name + ':' +str(rec.port) +'/xmlrpc/object', allow_none=True)
            account_ids = sock.execute(rec.db_name, user_id, rec.password, 'account.analytic.account', 'search', [])
            accounts = sock.execute(rec.db_name, user_id, rec.password, 'account.analytic.account', 'read', account_ids, [])
            for account in accounts:
                data = {}
                data['name'] = account.get('name')
                data['code'] = account.get('code')
                data['balance'] = account.get('balance')
                data['quantity'] = account.get('quantity')
                data['type'] = account.get('type')
                if account.get('partner_id', False):
                         partner_ids = partner_pool.search(cr, user_id, [('name','=', account['partner_id'][1])])
                         if partner_ids:
                             data['partner_id'] = partner_ids[0]
                if account.get('user_id', False):
                         user_ids = user_pool.search(cr, user_id, [('name','=', account['user_id'][1])])
                         if user_ids:
                             data['user_id'] = user_ids[0]
                account_pool.create(cr, uid , data, context=context)
        return True
        
    def import_project(self, cr, uid, ids, context=None):
        """
        This method can imports 'Project Data' from 6.0 to 7.0 AND Performs the 
        fields matching between these two files's data and model's columns.
        
        Returns common project fields's data..
        Add information into project form..
        """
        project_pool = self.pool.get('project.project')
        partner_pool = self.pool.get('res.partner')
        user_pool = self.pool.get('res.users')
        for rec in self.browse(cr, uid, ids, context=context):
            sock_comman = xmlrpclib.ServerProxy('http://' +rec.name + ':' + str(rec.port) +'/xmlrpc/common')
            user_id = sock_comman.login(rec.db_name, rec.user_name, rec.password)
            sock = xmlrpclib.ServerProxy('http://' +rec.name + ':' +str(rec.port) +'/xmlrpc/object', allow_none=True)
            project_ids = sock.execute(rec.db_name, user_id, rec.password, 'project.project', 'search', [])
            projects = sock.execute(rec.db_name, user_id, rec.password, 'project.project', 'read', project_ids, [])
            
            for project in projects:
                
#Check if Project Already Exists

                if  project_pool.search(cr, user_id, [('name','=',  project.get('name'))],context=context):
                    _logger.warning('Project %s  already exists  ', project.get('name'))
                    
# Create Project                   
                else: 
                    data = {}
                    data['name'] = project.get('name')
                    data['planned_hours'] = project.get('planned_hours')
                    data['effective_hours'] = project.get('effective_hours')
                    data['date_start'] = project.get('date_start')
                    data['date'] = project.get('date')
                    data['priority'] = project.get('priority')
                    data['state'] = project.get('state')
                    if project.get('partner_id', False):
                             partner_ids = partner_pool.search(cr, user_id, [('name','=', project['partner_id'][1])])
                             if partner_ids:
                                 data['partner_id'] = partner_ids[0]
                    if project.get('parent_id', False):
                             parent_ids =self.search(cr, user_id, [('name','=', project['parent_id'][1])])
                             if parent_ids:
                                 data['parent_id'] = parent_ids[0]
                    if project.get('user_id', False):
                             user_ids = user_pool.search(cr, user_id, [('name','=', project['user_id'][1])])
                             if user_ids:
                                 data['user_id'] = user_ids[0]
                    project_id= project_pool.create(cr, uid , data, context=context)
                    
                    self.import_attachment(cr, uid, ids, sock, user_id, project_id, 'project.project', context)
                    
        return True
    

    
    
    def import_task(self, cr, uid, ids, context=None):
        """
        This method can imports 'Task Data' from 6.0 to 7.0 AND Performs the 
        fields matching between these two files's data and model's columns.
        
        Returns common task fields's data..AND Also returns attachment of task with use of models of attachment..
        Add information into task form..
        """

        user_pool = self.pool.get('res.users')
        project_pool = self.pool.get('project.project')
        task_pool = self.pool.get('project.task')
        task_work_pool = self.pool.get('project.task.work')
        ir_attachment_pool = self.pool.get('ir.attachment')
        
        for rec in self.browse(cr, uid, ids, context=context):
            sock_comman = xmlrpclib.ServerProxy('http://' +rec.name + ':' + str(rec.port) +'/xmlrpc/common')
            user_id = sock_comman.login(rec.db_name, rec.user_name, rec.password)
            sock = xmlrpclib.ServerProxy('http://' +rec.name + ':' +str(rec.port) +'/xmlrpc/object', allow_none=True)
            
            _logger.info('Getting Task IDs' )
#            task_ids = sock.execute(rec.db_name, user_id, rec.password, 'project.task', 'search', [('id','=',2847)])
            task_ids = sock.execute(rec.db_name, user_id, rec.password, 'project.task', 'search', [('state','=','open')])
#            task_ids = sock.execute(rec.db_name, user_id, rec.password, 'project.task', 'search', [])
            tasks = sock.execute(rec.db_name, user_id, rec.password, 'project.task', 'read', task_ids, []) 
                      
            for task in tasks:

#Check if Task Already Exists 
                
#                if  task_pool.search(cr, user_id, [('name','=',  task.get('name'))],context=context):
#                    _logger.warning('Task %s  already exists Skipping ', task.get('name'))                
                
#                else:
                    data = {}
                    
                    _logger.info('Importing Task %s %s' , task.get('id'), task.get('name', ''))
                    
                    if task.get('name', False):
                        data['name'] = task.get('name', '')
                    else:
                        data['name'] = '/'
                    data['description'] = task.get('description')
                    data['planned_hours'] = task.get('planned_hours')
                    data['date_deadline'] = task.get('date_dateline')
                    data['progress'] = task.get('progress')
                    data['priority'] = task.get('priority')
                    data['sequence'] = task.get('sequence')
                    data['date_start'] = task.get('date_start')
                    data['date_end'] = task.get('date_end')

                    data['task_number'] = task.get('id')
                                      
                    if task.get('user_id', False):
							 user_ids = user_pool.search(cr, user_id, [('name','=', task['user_id'][1])])
							 if user_ids:
								 data['user_id'] = user_ids[0]
                    
                    if task.get('project_id', False):
                             project_ids = project_pool.search(cr, user_id, [('name','=', task['project_id'][1])])
                             if project_ids:
                                 data['project_id'] = project_ids[0]
                                 
                    if task.get('parent_id', False):
                             parent_ids = self.search(cr, uid, [('name','=', task['parent_id'][1])])
                             if parent_ids:
                                 data['parent_id'] = parent_ids[0]
                                 
                    
                    if task.get('state') == 'open':
                        data['stage_id'] = 4
                    elif task.get('state') == 'draft':
                        data['stage_id'] = 1
                    elif task.get('state') == 'pending':
                        data['stage_id'] = 2
                    elif task.get('state') == 'canceled':
                        data['stage_id'] = 8     
                    elif task.get('state') == 'done':
                        data['stage_id'] = 7                                
                    data['state'] = task.get('state')
                    
                    task_id = task_pool.create(cr, uid , data, context=context)  
                    self.import_attachment(cr, uid, ids, sock, user_id,task_id ,task.get('id'), 'project.task',  context=context)
                                      
                    work_ids = sock.execute(rec.db_name, user_id, rec.password, 'project.task.work', 'search', [('task_id','=',task.get('id'))])
                    worksummary = sock.execute(rec.db_name, user_id, rec.password, 'project.task.work', 'read', work_ids, [])
                    
                    n = 0
                    for work in worksummary:  
                         n = n+1
                         work_data = {}
                         work_data['name'] = work.get('name')
                         work_data['company_id'] = 1
                         work_data['hours'] = work.get('hours')
                         work_data['date'] = work.get('date')
                         work_data['task_id'] = int(task_id)
                         if work.get('user_id', False):
                             user_ids = user_pool.search(cr, uid, [('name','=', work['user_id'][1])])
                             if user_ids:
                                 work_data['user_id'] = user_ids[0]
                         project_task_work_id = task_work_pool.create(cr, uid ,work_data, context=context)
                         
                    _logger.info('Loaded %s Work Items',n)
                         
 
        return True
    
    def import_hr_expense(self, cr, uid, ids, context=None):
        
        hr_expense_pool = self.pool.get('hr.expense.expense')
        user_pool = self.pool.get('res.users')
        employee_pool = self.pool.get('hr.employee')
        hr_department = self.pool.get('hr.department')

        
        for rec in self.browse(cr, uid, ids, context=context):
            sock_comman = xmlrpclib.ServerProxy('http://' +rec.name + ':' + str(rec.port) +'/xmlrpc/common')
            user_id = sock_comman.login(rec.db_name, rec.user_name, rec.password)
            sock = xmlrpclib.ServerProxy('http://' +rec.name + ':' +str(rec.port) +'/xmlrpc/object', allow_none=True)
            expense_ids = sock.execute(rec.db_name, user_id, rec.password, 'hr.expense.expense', 'search', [])
            expenses = sock.execute(rec.db_name, user_id, rec.password, 'hr.expense.expense', 'read', expense_ids, [])
            for expense in expenses:
                
                _logger.info('Importing Hr Expense %s %s' , expense.get('id'), expense.get('name', ''))
                data = {}
                data['name'] = expense.get('name')
                data['state'] = expense.get('state')
                data['date'] = expense.get('date')
                data['date_valid'] = expense.get('date_valid')
                data['date_confirm'] = expense.get('date_confirm')
                data['quantity'] = expense.get('quantity')
                data['type'] = expense.get('type')
                
                if expense.get('user_id', False):
                         user_ids = user_pool.search(cr, user_id, [('name','=', expense['user_id'][1])])
                         if user_ids:
                             data['user_id'] = user_ids[0]
                if expense.get('user_valid', False):
                         user_ids = user_pool.search(cr, user_id, [('name','=', expense['user_valid'][1])])
                         if user_ids:
                             data['user_valid'] = user_ids[0]             
                if expense.get('employee_id', False):
                         employee_ids = employee_pool.search(cr, user_id, [('name','=', expense['employee_id'][1])])
                         if employee_ids:
                             data['employee_id'] = employee_ids[0]
                if expense.get('department_id', False):
                         department_ids = employee_pool.search(cr, user_id, [('name','=', expense['department_id'][1])])
                         if department_ids:
                             data['department_id'] = department_ids[0]
                hr_expense_id = hr_expense_pool.create(cr, uid , data, context=context)
                
                
                self.import_attachment(cr, uid, ids, sock, user_id, hr_expense_id, expense.get('id'),'hr.expense.expense', context=context)
                
                line_ids = sock.execute(rec.db_name, user_id, rec.password, 'hr.expense.line', 'search', ['expense_id','=',expense.get('id')])
                lines = sock.execute(rec.db_name, user_id, rec.password, 'hr.expense.line', 'read', line_ids, [])

                for line in lines:
                    data = {}
                    data['name'] = line.get('name')
                    data['state'] = line.get('state')
                    data['date'] = line.get('date')

                
        return True
    
    
    def import_attachment(self, cr, uid, ids, sock, user_id, task_id, res_id, res_model,  context=None):

        for rec in self.browse(cr, uid, ids, context=context):
            ir_attachment_pool = self.pool.get('ir.attachment')
            user_pool = self.pool.get('res.users')
            partner_pool = self.pool.get('res.partner')
     
            attachment_ids = sock.execute(rec.db_name, user_id, rec.password, 'ir.attachment', 'search', [('res_model','=',res_model),('res_id','=',res_id)])
            for attachment_id in attachment_ids:
                try:
                    attachment = sock.execute(rec.db_name, user_id, rec.password, 'ir.attachment', 'read', attachment_id, [])
                
                    
            
                    _logger.info('Getting attachment %s', attachment.get('datas_fname' ))
                    
                    attachment_data = {} 
               
                    attachment_data['datas'] = attachment.get('datas', '')
                    attachment_data['res_name'] = attachment.get('res_name')
                    attachment_data['datas_fname'] = attachment.get('datas_fname')
                    if attachment.get('datas_fname', False):
                        attachment_data['name'] = attachment.get('datas_fname')
                    elif attachment.get('name',False):
                        attachment_data['name'] = attachment.get('name')
            
                    attachment_data['store_fname'] = attachment.get('store_fname')
                    attachment_data['file_size'] = attachment.get('file_size')
                    attachment_data['file_type'] = attachment.get('file_type')
                    attachment_data['index_content'] = attachment.get('index_content')
                    attachment_data['url'] =attachment.get('url')
                    if attachment.get('partner_id', False):
                         partner_ids = partner_pool.search(cr, uid, [('name','=', attachment['partner_id'][1])])
                         if partner_ids:
                             attachment_data['partner_id'] = partner_ids[0]
                        
                    attachment_data['type'] = attachment.get('type')
                    attachment_data['company_id'] = 1
                    attachment_data['res_model'] = res_model
                    attachment_data['res_id'] = task_id
                    if attachment.get('user_id', False):
                         user_ids = user_pool.search(cr, uid, [('name','=', attachment['user_id'][1])])
                         if user_ids:
                             attachment_data['user_id'] = user_ids[0]
                    if attachment_data['name']:      
                        ir_attachment_id = ir_attachment_pool.create(cr, uid ,attachment_data, context=context)
                    else:
                        logger.error('No File Name  attachment skipped')
                except:
                    logger.error('Error Getting attachment %s skipped',attachment_id )


 
                        
        return   True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
