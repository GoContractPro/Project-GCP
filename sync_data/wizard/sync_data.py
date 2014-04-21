from osv import orm,fields,osv

from openerp.tools.translate import _

import xmlrpclib
import logging
import sys

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
         'db_name' : 'test_sync6',
         'user_name' : 'admin',
         'password' : 'admin'
    }
    
    
    def import_user(self, cr, uid, ids, context=None):
        """
        This method can imports 'UserData' from 6.0 to 7.0 AND Performs the 
        fields matching between these two files's data and model's columns.
        
        Returns common User fields's data..
        Add information into user form..
        """
        
        
        user_pool = self.pool.get('res.users')
        category_pool = self.pool.get('hr.employee.category')
        job_pool = self.pool.get('hr.job')
        department_pool = self.pool.get('hr.department')
        employee_pool = self.pool.get('hr.employee')
        
        for rec in self.browse(cr, uid, ids, context=context):
            try:
                sock_comman = xmlrpclib.ServerProxy('http://' +rec.name + ':' + str(rec.port) +'/xmlrpc/common')
                user_id = sock_comman.login(rec.db_name, rec.user_name, rec.password)
                sock = xmlrpclib.ServerProxy('http://' +rec.name + ':' +str(rec.port) +'/xmlrpc/object', allow_none=True)

# Get parent Categories                
                category_ids = sock.execute(rec.db_name, user_id, rec.password, 'hr.employee.category', 'search', [('parent_id', '=', False)])                                
                hr_categorys = sock.execute(rec.db_name, user_id, rec.password, 'hr.employee.category', 'read', category_ids, [])
                
                children = {}
# Import Parents                
                for hr_category in hr_categorys:
                    
                    data = {}
                    data['name'] = hr_category.get('name')
                    data['complete_name'] = hr_category.get('complete_name')
                    data['parent_id'] = hr_category.get('parent_id')
#                    data['child_ids'] = hr_category.get('child_ids')
                    rec_id = category_pool.create(cr, uid , data, context=context)
                    children[rec_id] = hr_category.get('child_ids')
 #import Children                   
                while children:
                    for child_ids in children:
                        rec_ids = children.get(child_ids)
                        hr_category = sock.execute(rec.db_name, user_id, rec.password, 'hr.employee.category', 'read', rec_ids, [])
                        
                        data = {}
                        data['name'] = hr_category.get('name')
                        data['complete_name'] = hr_category.get('complete_name')
                        data['parent_id'] = rec_id
                        rec_id=category_pool.create(cr, uid , data, context=context)
                        children[rec_id] = hr_category.get('child_ids')
# Get parent Departments                
                hr_department_ids = sock.execute(rec.db_name, user_id, rec.password, 'hr.department', 'search', [('parent_id', '=', False)])
                hr_departments = sock.execute(rec.db_name, user_id, rec.password, 'hr.department', 'read', hr_department_ids, [])
                
                children = {}
# Import Parents                
                for hr_department in hr_departments:
                    
                    data['complete_name'] = hr_department.get('complete_name')
                    data['company_id'] = hr_department.get('company_id')
                    data['note'] = hr_department.get('note') 
                    if hr_department.get('manager_id', False):
                         id = employee_pool.search(cr, user_id, [('name','=', hr_department['manager_id'][1])])
                         if id:
                             data['manager_id'] = id[0]
                    
                    id = department_pool.create(cr, uid , data, context=context)
                    
                    children[id] = hr_department.get('child_ids')
# Import Children                    
                    while children:
                        for child_ids in children:
                            data = {}
                            data['complete_name'] = hr_department.get('complete_name')
                            data['company_id'] = hr_department.get('company_id')
                            data['note'] = hr_department.get('note') 
                            data['parent_id'] = id
                            if hr_department.get('manager_id', False):
                                id = employee_pool.search(cr, user_id, [('name','=', hr_department['manager_id'][1])])
                                if id:
                                    data['manager_id'] = id[0]

                            
                            id = department_pool.create(cr, uid , data, context=context)
                            
                            children[id] = hr_department.get('child_ids')
                                              
                  
# Import hr_job  
                hr_job_ids =   department_ids = sock.execute(rec.db_name, user_id, rec.password, 'hr.job', 'search', [])     
                hr_jobs = sock.execute(rec.db_name, user_id, rec.password, 'hr.job', 'read', hr_job_ids, [])

                for hr_job in hr_jobs:
                    data = {}
                    data['name'] = hr_job.get('name')
                    data['no_of_recruitment'] = hr_job.get('no_of_recruitment')
                    data['description'] = hr_job.get('description')
                    data['requirements'] = hr_job.get('requirements')
                    data['state'] = hr_job.get('state')
                    if hr_job.get('department_id', False):
                        id = job_pool.search(cr, user_id, [('name','=', hr_job['department_id'][1])])
                        if id:
                            data['department_id'] = id[0]
                              
                    job_pool.create(cr, uid , data, context=context)   
                
# Import user                
                
                user_ids = sock.execute(rec.db_name, user_id, rec.password, 'res.users', 'search', [('id', '!=', 1)])
    
                
                for user_id in user_ids:
                    
                    user = sock.execute(rec.db_name, user_id, rec.password, 'res.users', 'read', user_id, [])
                    
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
                    
    # Import Employee         
                    
                    employee  = sock.execute(rec.db_name, user_id, rec.password, 'hr.employee', 'read', user_id, [])
                    
                    data = {}
                    data['name_related'] = employee.get('name_related')
                    data['country_id'] = 1
                    data['birthday'] = employee.get('birthday')
                    data['ssnid'] = employee.get('ssnid')
                    data['sinid'] = employee.get('sinid')
                    data['identification_id'] = employee.get('identification_id')
                    data['otherid'] = employee.get('otherid')
                    data['gender'] = employee.get('gender')
                    data['marital'] = employee.get('marital')
                    if employee.get('department_id', False):
                        id = employee_pool.search(cr, user_id, [('name','=', employee['department_id'][1])])
                        if id:
                            data['department_id'] = id[0]
    
                    data['name_related'] = employee.get('name_related')
     
                    data['work_phone'] = employee.get('work_phone')
                    data['mobile_phone'] = employee.get('mobile_phone')
                    data['work_email'] = employee.get('work_email')
    
                    data['parent_id'] = employee.get('parent_id')
    
                    data['passport_id'] = employee.get('passport_id')
                    data['color'] = employee.get('color')
                    data['city'] = employee.get('city')
                    data['login'] = employee.get('login')
                    
                    employee_pool.create(cr, uid , data, context=context)
    # TODO search                data['last_login'] = employee.get('last_login')
    # TODO search                if employee.get('category_ids')
    # TODO build Parent Child                data['notes'] = employee.get('notes')                
                    
            except:
                e = sys.exc_info()
                raise osv.except_osv(('Error!'), (e))
                return 
       
        return self.reopen_form(cr,uid,ids,context)

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
            try:
                sock_comman = xmlrpclib.ServerProxy('http://' +rec.name + ':' + str(rec.port) +'/xmlrpc/common')
                user_id = sock_comman.login(rec.db_name, rec.user_name, rec.password)
                sock = xmlrpclib.ServerProxy('http://' +rec.name + ':' +str(rec.port) +'/xmlrpc/object', allow_none=True)
                partner_ids = sock.execute(rec.db_name, user_id, rec.password, 'res.partner', 'search', [])
                partners = sock.execute(rec.db_name, user_id, rec.password, 'res.partner', 'read', partner_ids, [])
            except:
                raise osv.except_osv(_('Error!'), _('Your error message. %s',e))
                return
            
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
        return self.reopen_form(cr,uid,ids,context)
    
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
            try:
                
                sock_comman = xmlrpclib.ServerProxy('http://' +rec.name + ':' + str(rec.port) +'/xmlrpc/common')
                user_id = sock_comman.login(rec.db_name, rec.user_name, rec.password)
                sock = xmlrpclib.ServerProxy('http://' +rec.name + ':' +str(rec.port) +'/xmlrpc/object', allow_none=True)
                account_ids = sock.execute(rec.db_name, user_id, rec.password, 'account.analytic.account', 'search', [])
                accounts = sock(self,cr,uid,ids,context).execute(rec.db_name, user_id, rec.password, 'account.analytic.account', 'read', account_ids, [])
            except:
                raise osv.except_osv(_('Error!'), _('Your error message. %s',e))
                return
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
        analytic_pool = self.pool.get('account.analytic.account')
        project_pool = self.pool.get('project.project')
        partner_pool = self.pool.get('res.partner')
        user_pool = self.pool.get('res.users')
        task_pool = self.pool.get('project.task')
        work_pool = self.pool.get('project.task.work')
        
         
        for rec in self.browse(cr, uid, ids, context=context):
            try:
                """
                delete all work, task, project before import
                """
                work_ids = work_pool.search(cr, uid, [],context=context)
                work_pool.unlink(cr,uid,work_ids, context=context)
                task_ids = task_pool.search(cr, uid, [],context=context)
                task_pool.unlink(cr,uid,task_ids,context=context)
                project_ids = project_pool.search(cr, uid, [],context=context)
                project_pool.unlink(cr,uid,project_ids,context=context)
                analytic_pool.unlink(cr,uid,project_ids,context=context)
     
            
                sock_comman = xmlrpclib.ServerProxy('http://' +rec.name + ':' + str(rec.port) +'/xmlrpc/common')
                user_id = sock_comman.login(rec.db_name, rec.user_name, rec.password)
                sock = xmlrpclib.ServerProxy('http://' +rec.name + ':' +str(rec.port) +'/xmlrpc/object', allow_none=True)
                project_ids = sock.execute(rec.db_name, user_id, rec.password, 'project.project', 'search', [])
               
                
            except:
                e = sys.exc_info() 
                raise osv.except_osv(('Error!'), ('Your error message. %s',e))
                return            
            for project_id in project_ids:
                project = sock.execute(rec.db_name, user_id, rec.password, 'project.project', 'read', project_id, [])
                  

                data = {}
                data['name'] = project.get('name')
                data['write_date'] = project.get('write_date')
                data['create_date'] = project.get('create_date')
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
                project_id = project_pool.create(cr, uid, data, context=context)
                
 #               self.import_attachment(cr, uid, ids, sock,rec, user_id, project_id, project.get('id'), 'project.project', context=context)

                self.import_task(cr, uid, ids, sock, rec, user_id, project_id, project.get('tasks'), context=context)
   
        return self.reopen_form(cr,uid,ids,context)
    

    
    
    def import_task(self, cr, uid, ids, sock, rec, user_id, project_id, task_ids,  context=None):
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
        
        try:
           
            for task_id in task_ids:
                
    #            task_ids = sock.execute(rec.db_name, user_id, rec.password, 'project.task', 'search', [('id','=',2847)])
    #            task_ids = sock.execute(rec.db_name, user_id, rec.password, 'project.task', 'search', [('state','=','open')])

                task = sock.execute(rec.db_name, user_id, rec.password, 'project.task', 'read', task_id, [])     
    #Check if Task Already Exists 
    #            
    #            if  task_pool.search(cr, user_id, [('name','=',  task.get('name'))],context=context):
    #                _logger.warning('Task %s  already exists Skipping ', task.get('name'))                
                
    #           else:
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
                data['project_id'] = project_id
                data['task_number'] = task.get('id')
                                  
                if task.get('user_id', False):
						 user_ids = user_pool.search(cr, user_id, [('name','=', task['user_id'][1])])
						 if user_ids:
							 data['user_id'] = user_ids[0]
                    
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
                self.import_attachment(cr, uid, ids, sock, rec, user_id, task_id ,task.get('id'), 'project.task',  context=context)
                                  
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
                     
        except:
            e = sys.exc_info()
            raise osv.except_osv(('Error!'), (e))
            return 
        return self.reopen_form(cr,uid,ids,context)
    
    
    
    
    def import_hr_expense(self, cr, uid, ids, context=None):
        
        hr_expense_pool = self.pool.get('hr.expense.expense')
        user_pool = self.pool.get('res.users')
        employee_pool = self.pool.get('hr.employee')
        hr_department = self.pool.get('hr.department')

        
        for rec in self.browse(cr, uid, ids, context=context):
            try:
                sock_comman = xmlrpclib.ServerProxy('http://' +rec.name + ':' + str(rec.port) +'/xmlrpc/common')
                user_id = sock_comman.login(rec.db_name, rec.user_name, rec.password)
                sock = xmlrpclib.ServerProxy('http://' +rec.name + ':' +str(rec.port) +'/xmlrpc/object', allow_none=True)
                expense_ids = sock.execute(rec.db_name, user_id, rec.password, 'hr.expense.expense', 'search', [])
                expenses = sock.execute(rec.db_name, user_id, rec.password, 'hr.expense.expense', 'read', expense_ids, [])
            except:
                e = sys.exc_info()
                raise osv.except_osv(('Error!'), (e))
                return                
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
                
                
                self.import_attachment(cr, uid, ids, sock, rec, user_id, hr_expense_id, expense.get('id'),'hr.expense.expense', context=context)
                
                line_ids = sock.execute(rec.db_name, user_id, rec.password, 'hr.expense.line', 'search', ['expense_id','=',expense.get('id')])
                lines = sock.execute(rec.db_name, user_id, rec.password, 'hr.expense.line', 'read', line_ids, [])

                for line in lines:
                    data = {}
                    data['name'] = line.get('name')
                    data['date_value'] = line.get('date_value')
                    data['expense_id'] = line.get('expense_id')
                    data['unit_amount'] = line.get('unit_amount')
                    data['unit_quantity'] = line.get('unit_quantity')
# TODO check if Product Exist if not Create
                    data['product_id'] = line.get('product_id')
# TODO check uom exist if not Create                    
                    data['uom_id'] = line.get('uom_id')
                    data['description'] = line.get('description')
# TODO check if analytic_accouont exist if not create
                    data['analytic_account'] = line.get('analytic_account')
                    data['ref'] = line.get('ref')
                    data['sequence'] = line.get('sequence')
                    


                
        return True
    
    
    def import_attachment(self, cr, uid, ids, sock, rec, user_id, res_id7, res_id6, res_model,  context=None):


            try:
                ir_attachment_pool = self.pool.get('ir.attachment')
                user_pool = self.pool.get('res.users')
                partner_pool = self.pool.get('res.partner')
                attachment_ids = sock.execute(rec.db_name, user_id, rec.password, 'ir.attachment', 'search', [('res_model','=',res_model),('res_id','=',res_id6)])
            except:
                e = sys.exc_info()
                raise osv.except_osv(('Error!'), (e))
                return                
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
                    attachment_data['res_id'] = res_id7
                    if attachment.get('user_id', False):
                         user_ids = user_pool.search(cr, uid, [('name','=', attachment['user_id'][1])])
                         if user_ids:
                             attachment_data['user_id'] = user_ids[0]
                    if attachment_data['name']:      
                        ir_attachment_id = ir_attachment_pool.create(cr, uid ,attachment_data, context=context)
                    else:
                        _logger.error('No File Name  attachment skipped')
                except:
                    e = sys.exc_info()
                    _logger.error('Error Getting attachment %s skipped',attachment_id, e  )
                    
                return
           
            return   True 
    
    def reopen_form(self,cr,uid,ids,context):
        view_id = self.pool.get('ir.ui.view').search(cr,uid,[('model','=','sync.data')])
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sync.data',
            'name': 'Sync Data',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
            'context': context
            }
        
      
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
