SELECT 
  account_analytic_account.name, 
  project_project.planned_hours, 
  project_project.effective_hours, 
  account_analytic_account.description, 
  account_analytic_account.code, 
  account_analytic_account.x_manager_id, 
  account_analytic_account.state, 
  account_analytic_account.user_id, 
  project_project.x_manager_id, 
  res_users.name AS "user"
FROM 
  public.account_analytic_account, 
  public.project_project, 
  public.res_users
WHERE 
  account_analytic_account.id = project_project.analytic_account_id AND
  account_analytic_account.user_id = res_users.id;
