UPDATE  public.account_analytic_account
 set name = id|| ' ' || name 
WHERE 
  name IN (
  SELECT t.name FROM public.account_analytic_account t
  GROUP BY t.name HAVING COUNT(*) >1
  );

