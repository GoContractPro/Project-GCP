# -*- coding: utf-8 -*-
from osv import fields, osv
from tools.translate import _

class projectProjectInehrit(osv.osv):
    _inherit = 'project.project'
    _columns = {
        'is_scrum': fields.boolean("Is it a Scrum Project ?"),
        'scrum_master_id': fields.many2one('res.users', 'Scrum Master', 
                 help="""The Scrum Master doesn't manage the team that produces the work, \
                 instead he supports the Product Owner, coaches the team and makes sure that \
                 Scrum processes are adhered to. The Scrum Master is responsible for the Scrum process,\ 
                 its correct implementation, and the maximization of its benefits."""),
        'product_owner_id': fields.many2one('res.users', "Product Owner",
                  help="""Part of the product owner responsibilities is to have a vision of what he or she wishes to build, \
                   and convey that vision to the scrum team. This is key to successfully starting any agile software development project. \
                   The agile product owner does this in part through the product backlog, which is a prioritized features list \
                   for the product."""
                  ),
        'goal' : fields.text("Goal", help="The document that includes the project, jointly between the team and the customer"),
    }
    _defaults = {
        'is_scrum': True,
    }

