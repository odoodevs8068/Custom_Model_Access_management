from odoo import models, fields, api


class IrExports(models.Model):
    _inherit = "ir.exports"

    user_ids = fields.Many2many('res.users', string="Users ")