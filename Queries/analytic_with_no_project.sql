SELECT 
  account_analytic_account.name, 
  account_analytic_account.state, 
  account_analytic_account.date_start

  
FROM 
  public.account_analytic_account

WHERE 

  account_analytic_account.id not in ( select analytic_account_id
					from project_project
					where analytic_account_id is not null );
