import time
from report import report_sxw
from osv import osv
import pooler

 
class srs_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(srs_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
            'get_srs_lines':self.get_srs_lines
        })
    def get_srs_lines(self,o):
       result=[]  
       for dline in req_obj.browse(self.cr,self.uid,self.ids): 
                project_id=dline.project_id.id  
                for rline in  dline.doc_req_line: 
                    for req in rline.srequirement_ids:
                        code=req.name
                        sname=req.sname
       return result    
report_sxw.report_sxw('report.srs_report', 'srs.document', 'addons/npg_srs/report/srs_report.rml', parser=srs_report, header=True)

