SELECT 
  ir_module_module.name, 
   
  ir_module_module.shortdesc, 
  ir_module_module.author
FROM 
  public.ir_module_module
WHERE 
  ir_module_module.state = 'installed'
ORDER BY
  ir_module_module.name ASC;
