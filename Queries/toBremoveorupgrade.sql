SELECT 
  ir_module_module.state, 
  ir_module_module.author, 
  ir_module_module.name, 
  ir_module_module.description
FROM 
  public.ir_module_module
WHERE 
  ir_module_module.state not IN ('installed','uninstalled');
