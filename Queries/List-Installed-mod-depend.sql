SELECT 
  ir_module_module_dependency.name, 
  ir_module_module_dependency.version_pattern, 
  ir_module_module.state, 
  ir_module_module.author, 
  ir_module_module.name, 
  ir_module_module.description, 
  ir_module_module.views_by_module
FROM 
  public.ir_module_module_dependency, 
  public.ir_module_module
WHERE 
  ir_module_module.id = ir_module_module_dependency.module_id AND
  ir_module_module.state = 'installed'
