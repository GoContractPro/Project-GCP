import time
 
from openerp.report import report_sxw
 
class srs_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(srs_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
             
        })
report_sxw.report_sxw('report.srs_report', 'srs.document', 'addons/npg_srs/report/srs_report.rml', parser=srs_report, header=True)

