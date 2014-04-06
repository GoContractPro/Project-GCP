UPDATE  public.project_task
 set name = id|| ' ' || name 
WHERE 
  name IN (
  SELECT t.name FROM public.project_task t
  GROUP BY t.name HAVING COUNT(*) >1
  );

