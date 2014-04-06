COPY (SELECT 
  
  name,
  active
FROM 
  public.res_users
where res_users.active = False)
to '/tmp/users-active.csv'
WITH CSV HEADER ;

update public.res_users
set res_users.active =True;