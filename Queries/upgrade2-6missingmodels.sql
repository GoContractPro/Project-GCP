
delete from ir_model where model = 'res.partner.canal' ;
delete from ir_model where model = 'partner.wizard.spam' ;
delete from ir_model where model = 'res.config.users' ;
delete from ir_model where model = 'res.config.view' ;
delete from ir_model where model = 'email_template.mailbox' ;
delete from ir_model where model = 'base.setup.installer' ;
delete from ir_model where model = 'base.setup.company' ;
delete from ir_model where model = 'base.setup.config' ;
delete from ir_model where model = 'marketing.installer' ;
delete from ir_model where model = 'mailgate.thread' ;
delete from ir_model where model = 'mailgate.message' ;
delete from ir_model where model = 'email.server.tools' ;
delete from ir_model where model = 'calendar.event.edit.all' ;
delete from ir_model where model = 'base.calendar.set.exrule' ;
delete from ir_model where model = 'board.note.type' ;
delete from ir_model where model = 'board.note' ;
delete from ir_model where model = 'misc_tools.installer' ;
delete from ir_model where model = 'report_designer.installer' ;
delete from ir_model where model = 'crm.installer' ;
delete from ir_model where model = 'crm.send.mail.attachment' ;
delete from ir_model where model = 'crm.send.mail' ;
delete from ir_model where model = 'crm.lead2opportunity' ;
delete from ir_model where model = 'crm.lead2opportunity.action' ;
delete from ir_model where model = 'knowledge.installer' ;
delete from ir_model where model = 'email_template.account' ;
delete from ir_model where model = 'email_template.send.wizard' ;
delete from ir_model where model = 'email.server' ;
delete from ir_model where model = 'project.installer' ;
delete from ir_model where model = 'project.task.close' ;
delete from ir_model where model = 'hr.employee.marital.status' ;
delete from ir_model where model = 'hr.installer' ;
delete from ir_model where model = 'account.installer.modules' ;
delete from ir_model where model = 'account.analytic.Journal.report' ;
delete from ir_model where model = 'account.bs.report' ;
delete from ir_model where model = 'account.pl.report' ;
delete from ir_model where model = 'stock.move.track' ;
delete from ir_model where model = 'stock.move.split.lines.exist' ;
delete from ir_model where model = 'stock.move.memory.out' ;
delete from ir_model where model = 'stock.move.memory.in' ;
delete from ir_model where model = 'stock.replacement' ;
delete from ir_model where model = 'stock.replacement.result' ;
delete from ir_model where model = 'stock.ups' ;
delete from ir_model where model = 'stock.ups.final' ;
delete from ir_model where model = 'stock.ups.upload' ;
delete from ir_model where model = 'purchase.installer' ;
delete from ir_model where model = 'sale.installer' ;
delete from ir_model where model = 'hr.contract.wage.type.period' ;
delete from ir_model where model = 'hr.contract.wage.type' ;
delete from ir_model where model = 'hr.passport' ;
delete from ir_model where model = 'hr.payroll.register' ;
delete from ir_model where model = 'hr.payroll.advice' ;
delete from ir_model where model = 'hr.payroll.advice.line' ;
delete from ir_model where model = 'hr.contibution.register' ;
delete from ir_model where model = 'hr.contibution.register.line' ;
delete from ir_model where model = 'hr.allounce.deduction.categoty' ;
delete from ir_model where model = 'company.contribution' ;
delete from ir_model where model = 'company.contribution.line' ;
delete from ir_model where model = 'hr.payslip.line.line' ;
delete from ir_model where model = 'hr.payroll.employees.detail' ;
delete from ir_model where model = 'hr.payroll.year.salary' ;
delete from ir_model where model = 'res.partner.job' ;
delete from ir_model where model = 'base.contact.installer' ;
delete from ir_module_module where name = 'modules.graph'

delete from res_groups_users_rel where gid = 16;
delete from res_groups where id = 16;


--2014-03-02 05:31:48,833 27196 WARNING npgcore603 openerp.modules.loading: Starting a new iteration of selecting modules to upgrade
--2014-03-02 05:31:48,916 27196 WARNING npgcore603 openerp.modules.graph: Some modules were not loaded.


