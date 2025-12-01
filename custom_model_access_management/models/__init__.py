from . import access_right
from . import ir_exports


from odoo import models
from odoo.http import  request

def check_disable_debug_mode(user):
    if not user:
        user = request.env['res.users'].sudo().browse(request.session.uid)
        return user.has_group('custom_model_access_management.group_disable_debug') if user else False

class HttpInherit(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _handle_debug(cls):
        if 'debug' in request.httprequest.args:
            if not check_disable_debug_mode(request.env.user):
                return super(HttpInherit, cls)._handle_debug()
            request.session.debug = ''