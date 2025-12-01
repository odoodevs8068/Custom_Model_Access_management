import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree
import logging

_logger = logging.getLogger(__name__)

#
# class IrModelInherit(models.Model):
#     _inherit = 'ir.model'
#
#     model_access_right_ids = fields.One2many('model_access.right', 'model_id')


class ModelAccessRight(models.Model):
    _name = 'model_access.right'
    _inherit = 'mail.thread'
    _description = 'Manage Modules Access Control'
    _rec_name = 'model_id'

    type = fields.Selection(
        [
            ('model_access_control', 'User Model Access'),
            ('gl_model_access_control', 'Model Access'),
            ('show_field', 'Restrict Export Fields'),
        ], string='Access Type', default='model_access_control', tracking=True,  required=True
    )
    model_id = fields.Many2one('ir.model',ondelete='cascade', string="Model", tracking=True,help="Select the model")
    model_name = fields.Char(related='model_id.model', store=True)

    user_id = fields.Many2one('res.users', string="Users")
    is_create = fields.Boolean(string="Hide Create", tracking=True, help="Hide the Create option")
    is_edit = fields.Boolean(string="Hide Edit", tracking=True, help="Hide the Edit option")
    is_delete = fields.Boolean(string="Hide Delete", help="Hide the delete option")
    is_export = fields.Boolean(string="Hide Export", tracking=True, help="Hide the Export All option")
    is_archive = fields.Boolean(string="Hide Archive/UnArchive", tracking=True, help="Hide the Archive option")
    is_duplicate = fields.Boolean(string="Hide Duplicate", tracking=True, help="Hide the Duplicate option")
    is_import = fields.Boolean(string="Hide Import", tracking=True, help="Hide the Import option")
    is_addProperty = fields.Boolean(string="Hide Add a Properties", tracking=True, help="Hide the Add a Properties option")
    show_import = fields.Boolean("Hide Upload Button")


    #Views
    hide_searchbar = fields.Boolean("Hide SearchBar")
    hide_filter_section = fields.Boolean("Hide Filter Section")
    hide_group_by_section = fields.Boolean("Hide Group BY Section")
    hide_favorites_section = fields.Boolean("Hide Favorites Section")

    server_action_ids = fields.Many2many('ir.actions.server')
    report_action_ids = fields.Many2many('ir.actions.report')
    act_window_ids = fields.Many2many('ir.actions.act_window')
    header_button_ids = fields.One2many('model_header_button', 'model_access_id')
    page_ids = fields.One2many('model_notebook_page', 'model_access_id')

    field_ids = fields.Many2many('ir.model.fields', tracking=True)

    export_fields_ids = fields.Many2many(
        'ir.model.fields',
        'ir_model_fields_export_hide_rel',
        'model_id',
        'field_id',
        string='Hide Export Fields'
    )
    export_templates_ids = fields.Many2many(
        "ir.exports",
        'ir_export_templates_hide_rel',
        'model_id',
        'export_id',
        string="Hide Export Templates")

    hide_chatter_section = fields.Boolean("Hide Chatter Section")
    hide_send_mssge = fields.Boolean("Hide Send Message Button")
    hide_log_note = fields.Boolean("Hide Log Note Button")
    hide_activities = fields.Boolean("Hide Activities Button")
    hide_attachment = fields.Boolean("Hide Attachment Button")
    hide_chatter_edit = fields.Boolean("Hide Chatter Edit Option")
    hide_chatter_delete = fields.Boolean("Hide Chatter Delete Option")
    o_attachment_preview = fields.Boolean("Add Attachment Preview")
    remove_attachment_preview = fields.Boolean("Remove Attachment Preview")

    # Global Export Fields Restrictions

    field_id = fields.Many2one("ir.model.fields", string="Export Field")
    user_ids = fields.Many2many("res.users", 'Users')
    view_id = fields.Many2one('ir.ui.view', "View ID", readonly=True)


    @api.constrains('model_id')
    def _check_duplicate_model(self):
        for rec in self:
            if rec.model_id:
                existing = self.search([
                    ('model_id', '=', rec.model_id.id),
                    ('user_id', '=', rec.user_id.id),
                    ('id', '!=', rec.id),
                    ('type', '=', rec.type)
                ], limit=1)
                if existing:
                    raise UserError(_(f"Configuration already exists for {rec.model_id.name}"))

    @api.constrains('field_id')
    def _check_duplicate_field(self):
        for rec in self:
            if rec.field_id:
                existing = self.search([
                    ('field_id', '=', rec.field_id.id),
                    ('id', '!=', rec.id),
                    ('type', '=', 'show_field')
                ], limit=1)
                if existing:
                    raise UserError(_("Configuration already exists for Field %s ") % rec.field_id.field_description)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.field_ids:
                rec._update_field_hiding()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'field_ids' in vals:
            for rec in self:
                rec._update_field_hiding()
        return res

    def _update_field_hiding(self):
        """Add/remove users from field groups and update form/list/kanban views"""
        module_name_for_imd = 'custom_model_access_management'

        def _field_exists_in_view(view, field_name):
            """Check if a field exists anywhere in the view's XML"""
            if not view.arch_base:
                return False
            try:
                doc = etree.fromstring(view.arch_base)
                return bool(doc.xpath(f".//field[@name='{field_name}']"))
            except Exception as e:
                _logger.warning("Error parsing view %s: %s", view.name, e)
                return False

        for rec in self:
            if not rec.model_id or not rec.user_id:
                continue

            model_name = rec.model_id.model
            user = rec.user_id
            current_field_names = set(f.name for f in rec.field_ids)

            field_groups = self.env['res.groups'].search([
                ('name', 'like', f"auto_hide_field_{model_name.replace('.', '_')}_")
            ])
            existing_field_names = {
                g.name.replace(f"auto_hide_field_{model_name.replace('.', '_')}_", ""): g
                for g in field_groups
            }

            for field in rec.field_ids:
                field_name = field.name
                group_name = f"auto_hide_field_{model_name.replace('.', '_')}_{field_name}"
                group = existing_field_names.get(field_name)
                if not group:
                    group = self.env['res.groups'].create({
                        'name': group_name,
                        'users': [(4, user.id)]
                    })
                else:
                    if user.id not in group.users.ids:
                        group.users = [(4, user.id)]

                imd = self.env['ir.model.data'].search([
                    ('model', '=', 'res.groups'),
                    ('res_id', '=', group.id),
                    ('module', '=', module_name_for_imd)
                ], limit=1)
                if not imd:
                    imd = self.env['ir.model.data'].create({
                        'module': module_name_for_imd,
                        'name': group_name,
                        'model': 'res.groups',
                        'res_id': group.id,
                        'noupdate': True,
                    })
                group_xml_id = f"{imd.module}.{imd.name}"

                views = self.env['ir.ui.view'].search([
                    ('model', '=', model_name),
                    ('type', 'in', ('form', 'list', 'kanban')),
                ], order='priority desc')

                field_found = False
                for view in views:
                    if _field_exists_in_view(view, field_name):
                        try:
                            doc = etree.fromstring(view.arch_base)
                            field_node = doc.xpath(f".//field[@name='{field_name}']")
                            if field_node:
                                existing_groups = field_node[0].get("groups") or ""
                            else:
                                existing_groups = ""
                        except Exception as e:
                            _logger.warning("Error parsing view %s: %s", view.name, e)
                            existing_groups = ""

                        if existing_groups:
                            new_groups = f"{existing_groups},!{group_xml_id}"
                        else:
                            new_groups = f"!{group_xml_id}"

                        xpath = (
                            f"<xpath expr=\"//field[@name='{field_name}']\" position=\"attributes\">"
                            f"<attribute name=\"groups\">{new_groups}</attribute>"
                            f"</xpath>"
                        )
                        arch_base = "<data>\n" + xpath + "\n</data>"
                        view_name = f"auto_hide_{model_name.replace('.', '_')}_field_{field_name}_{view.id}"

                        existing_inherit = self.env['ir.ui.view'].search([('name', '=', view_name)], limit=1)
                        if existing_inherit:
                            existing_arch = existing_inherit.arch_base or ''
                            if xpath not in existing_arch:
                                existing_arch += '\n' + xpath
                                existing_inherit.write({'arch_base': existing_arch})
                        else:
                            self.env['ir.ui.view'].create({
                                'name': view_name,
                                'type': view.type,
                                'model': model_name,
                                'inherit_id': view.id,
                                'arch_base': arch_base,
                            })
                        field_found = True
                        break

                if not field_found:
                    _logger.info(
                        "Field '%s' not found in any form/list/kanban views for model '%s'. Skipping hiding.",
                        field_name, model_name
                    )

            for field_name, group in existing_field_names.items():
                if field_name not in current_field_names and user.id in group.users.ids:
                    group.users = [(3, user.id)]

    def unlink(self):
        module_name_for_imd = 'custom_model_access_management'
        for rec in self:
            model_name = rec.model_id.model
            user = rec.user_id
            for field in rec.field_ids:
                field_name = field.name
                group_name = f"auto_hide_field_{model_name.replace('.', '_')}_{field_name}"

                other_records = self.search([
                    ('id', '!=', rec.id),
                    ('field_ids', 'in', field.id),
                ])

                group = self.env['res.groups'].search([('name', '=', group_name)], limit=1)
                if not group:
                    continue
                if other_records:
                    if user.id in group.users.ids:
                        group.users = [(3, user.id)]
                else:
                    view_name = f"auto_hide_{model_name.replace('.', '_')}_field_{field_name}_"
                    view_inherits = self.env['ir.ui.view'].search([('name', 'like', view_name)])
                    view_inherits.unlink()
                    group.unlink()
        return super().unlink()

    @api.model
    def get_bulk_access(self, model):
        """Consolidated access rights for frontend."""
        result = self.hide_buttons( model)
        return result

    def default_access_return(self):
        return  {
            'is_delete': False,
            'is_export': False,
            'is_create': False,
            'is_edit': False,
            'is_archive': False,
            'is_duplicate': False,
            'is_import': False,
            'is_addProperty': False,
            'upload_access': False,
            'hide_searchbar': False,
            'hide_filter_section': False,
            'hide_group_by_section': False,
            'hide_favorites_section': False,
            'hide_send_mssge': False,
            'hide_log_note': False,
            'hide_activities': False,
            'hide_attachment': False,
            'hide_chatter_edit': False,
            'hide_chatter_delete': False,
            'hide_chatter_section': False,
            'o_attachment_preview': False,
            'remove_attachment_preview': False,
        }

    def get_configuration_model_access(self):
        show_import = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.show_import')
        is_export = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.is_export')
        is_addProperty = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.is_addProperty')
        is_archive = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.is_archive')
        is_duplicate = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.is_duplicate')
        is_import = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.is_import')
        return show_import, is_export, is_addProperty, is_archive, is_duplicate, is_import

    def get_configuration_chatter_access(self):
        hide_chatter_section = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.hide_chatter_section')
        hide_send_mssge = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.hide_send_mssge')
        hide_log_note = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.hide_log_note')
        hide_activities = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.hide_activities')
        hide_attachment = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.hide_attachment')
        hide_chatter_edit = self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.hide_chatter_edit')
        hide_chatter_delete =self.env['ir.config_parameter'].sudo().get_param('custom_model_access_management.hide_chatter_delete')
        return hide_chatter_section, hide_send_mssge, hide_log_note, hide_activities, hide_attachment, hide_chatter_edit, hide_chatter_delete

    def get_access_record(self, modelname, type):
        return self.sudo().search([
            ('model_id.model', '=', modelname),
            ('user_id', '=',  self._uid), ('type', '=', type)
        ], limit=1)

    def hide_buttons(self, model_name):
        access = self.default_access_return()
        access_record = self.get_access_record( model_name, 'model_access_control')
        access = self.get_gl_model_access_control(model_name, access, access_record)
        return access

    def get_gl_model_access_control(self, modelname, access, access_record):
        show_import, is_export, is_addProperty, is_archive, is_duplicate , is_import = self.get_configuration_model_access()
        hide_chatter_section, hide_send_mssge, hide_log_note, hide_activities, hide_attachment, hide_chatter_edit, hide_chatter_delete = self.get_configuration_chatter_access()
        gl_chatter = self.sudo().search([
            ('model_id.model', '=', modelname),
            ('type', '=', 'gl_model_access_control')
        ])

        def resolve_access(field, config=None):
            if config:
                return True
            if gl_chatter:
                if access_record:
                    return gl_chatter[field] if gl_chatter[field] else access_record[field]
                else:
                    return gl_chatter[field]
            else:
                return access_record[field] if access_record else False

        access['is_delete'] = resolve_access('is_delete')
        access['is_edit'] = resolve_access('is_edit')
        access['is_create'] = resolve_access('is_create')
        access['hide_searchbar'] = resolve_access('hide_searchbar')
        access['hide_filter_section'] = resolve_access('hide_filter_section')
        access['hide_group_by_section'] = resolve_access('hide_group_by_section')
        access['hide_favorites_section'] = resolve_access('hide_favorites_section')
        access['o_attachment_preview'] = resolve_access('o_attachment_preview')
        access['remove_attachment_preview'] = resolve_access('remove_attachment_preview')

        access['is_export'] = resolve_access('is_export', is_export)
        access['is_archive'] = resolve_access('is_archive', is_archive)
        access['is_import'] = resolve_access('is_import', is_import)
        access['is_duplicate'] = resolve_access('is_duplicate', is_duplicate)
        access['is_addProperty'] = resolve_access('is_addProperty', is_addProperty)
        access['upload_access'] = resolve_access('show_import', show_import)
        access['hide_send_mssge'] = resolve_access('hide_send_mssge', hide_send_mssge)
        access['hide_log_note'] = resolve_access('hide_log_note', hide_log_note)
        access['hide_activities'] = resolve_access('hide_activities', hide_activities)
        access['hide_attachment'] = resolve_access('hide_attachment', hide_attachment)
        access['hide_chatter_edit'] = resolve_access('hide_chatter_edit', hide_chatter_edit)
        access['hide_chatter_delete'] = resolve_access('hide_chatter_delete', hide_chatter_delete)
        access['hide_chatter_section'] = resolve_access('hide_chatter_section', hide_chatter_section)

        return access

    def get_gl_access_record(self, modelname, type):
        return self.sudo().search([
            ('model_id.model', '=', modelname), ('type', '=', type)
        ], limit=1)

    @api.model
    def get_server_actions(self,  model_name):
        access_record = self.get_access_record( model_name, 'model_access_control')
        gl_access_record = self.get_gl_access_record( model_name, 'gl_model_access_control')
        action_ids = []
        if gl_access_record:
            action_ids.extend(gl_access_record.server_action_ids.ids)
            action_ids.extend(gl_access_record.act_window_ids.ids)
        if access_record:
            action_ids.extend(access_record.server_action_ids.ids)
            act_ids = access_record.act_window_ids.ids
            action_ids.extend(act_ids)
        return action_ids


    @api.model
    def get_print_actions(self,  model_name):
        access_record = self.get_access_record( model_name, 'model_access_control')
        gl_access_record = self.get_gl_access_record(model_name, 'gl_model_access_control')
        report_ids = []
        if gl_access_record:
            report_ids.extend(gl_access_record.report_action_ids.ids)
        if access_record:
            report_ids.extend(access_record.report_action_ids.ids)
        return report_ids

    @api.model
    def get_hidden_header_buttons(self, model_name):
        access_record = self.get_access_record( model_name, 'model_access_control')
        gl_access_record = self.get_gl_access_record(model_name, 'gl_model_access_control')
        result = []
        if gl_access_record:
            gl_names = [x.technical_name for x in gl_access_record.header_button_ids]
            result.extend(gl_names)
        if access_record:
            names = [x.technical_name for x in access_record.header_button_ids]
            result.extend(names)
        return result

    def get_string_record(self, model_name, search_model):
        return self.sudo().env[search_model].search([
                    ('model_access_id.model_id.model', '=', model_name),
                    ('model_access_id.user_id' , '=', self.env.user.id)
                ])

    @api.model
    def get_form_notebook_page(self, model_name):
        records = self.get_string_record(model_name, 'model_notebook_page')
        gl_access_record = self.get_gl_access_record(model_name, 'gl_model_access_control')
        result = []
        if gl_access_record:
            gl_names = [x.name for x in gl_access_record.page_ids]
            result.extend(gl_names)
        if records:
            names = [x.name for x in records]
            result.extend(names)
        return result if len(result) > 0 else False

    @api.model
    def get_hide_templates(self, model_name):
        records = self.sudo().env['model_access.right'].search([
           ('model_id.model', '=', model_name) ,
            ('export_templates_ids' , '!=', []), ('user_id', '=', self._uid)
        ])
        if records:
            return records.export_templates_ids.ids
        return []

    def add_attachment_preview(self):
            view_ids = self.env['ir.ui.view'].sudo().search([
                ('type', '=', 'form'),
                ('model', '=', self.model_name),
            ])
            any_chatter = []
            any_attachment_preview = []
            to_inherit_view = False
            for view in view_ids:
                try:
                    xml = etree.fromstring(view.arch_db.encode('utf-8'))
                    chatter_nodes = xml.xpath(".//chatter | .//div[contains(@class, 'oe_chatter')]")
                    has_chatter = bool(chatter_nodes)
                    attachment_nodes = xml.xpath(".//div[contains(@class, 'o_attachment_preview')]")
                    has_attachment_preview = bool(attachment_nodes)
                    any_chatter.append(has_chatter)
                    any_attachment_preview.append(has_attachment_preview)

                    if has_chatter:
                        to_inherit_view = view

                except Exception as e:
                    print("Error parsing XML for view %s (ID %s): %s" % (view.name, view.id, e))

            if True  in any_attachment_preview:
                raise ValidationError(_("Sorry Already Attachment Preview Exist For This Model"))

            if True not in any_chatter:
                raise ValidationError(_("Sorry To Add Attachment Preview Chatter Section Required. This Model Doesnt Contains Chatter Section"))

            if (True in any_chatter) and (True not in any_attachment_preview):
                self.create_attachemet_preview_view(to_inherit_view)

    def button_remove_attachment_preview(self):
        self.remove_o_attachment_preview_view()
        self.o_attachment_preview = False

    def remove_o_attachment_preview_view(self):
        if self.view_id:
            self.view_id.unlink()

    def create_attachemet_preview_view(self, external_view):
        xpath = (
            f"<xpath expr=\"//chatter\" position=\"before\">"
                f"<div class=\"o_attachment_preview\"/>"
            f"</xpath>"
        )
        arch_base = "<data>\n" + xpath + "\n</data>"
        view_name = f"custom_{self.model_name.replace('.', '_')}_attachment_preview"
        view_identifier = f"attachment_preview_{self.model_name.replace('.', '_')}_form_inherit"
        if external_view:
            created_view_id = self.env['ir.ui.view'].create({
                'name': view_name,
                'type': 'form',
                'model': self.model_name,
                'inherit_id': external_view.id,
                'arch_base': arch_base,
            })
            if created_view_id:
                self.write({
                    'view_id' : created_view_id.id,
                    'o_attachment_preview' : True
                })
                data_id = self.env['ir.model.data'].create({
                    'module': 'custom_model_access_management',
                    'name': view_identifier,
                    'model': 'ir.ui.view',
                    'display_name': view_name,
                    'res_id': created_view_id,
                    'complete_name': f"custom_model_access_management.{view_identifier}",
                    'noupdate': True
                })



class ResGroupsView(models.Model):
    _inherit = 'res.groups'

    def get_application_groups(self, domain):
        domain += [('name', 'not ilike', 'auto_hide_')]
        return super(ResGroupsView, self).get_application_groups(domain)


class NotebookPages(models.Model):
    _name = "model_notebook_page"

    name = fields.Char("Page Name")
    model_access_id = fields.Many2one("model_access.right")


class HeaderButton(models.Model):
    _name = "model_header_button"

    name = fields.Char("Header Button Name")
    model_access_id = fields.Many2one("model_access.right")
    technical_name = fields.Char('technical name')
    type = fields.Char('Button type')
    view_type = fields.Char('Button type')

    @api.model
    def get_button_data(self, access_model_id):
        if access_model_id:
            access_model = self.sudo().env['model_access.right'].browse(access_model_id)
            button_data = self.get_model_buttons(access_model.model_id.model, access_model_id)
            return button_data
        return []

    def get_model_buttons(self, model_name, access_model_id):
        buttons = []

        View = self.env['ir.ui.view']
        view_types = ['form', 'list', 'kanban']
        views = View.search([ ('model', '=', model_name),  ('type', 'in', view_types), ])

        if not views:
            return []
        for view in views:
            try:
                arch_node = view._get_combined_arch()

                if isinstance(arch_node, str):
                    xml_root = etree.fromstring(arch_node.encode("utf-8"))
                else:
                    xml_root = arch_node

                button_nodes = xml_root.xpath("//button[@name]")
                for button in button_nodes:
                    technical_name = button.get("name")
                    string = button.get("string") or technical_name
                    button_type = button.get("type")

                    if not technical_name:
                        continue

                    button_exist = self.sudo().search([
                        ('model_access_id', '=', access_model_id),
                        ('technical_name', '=', technical_name),
                        ('type', '=', button_type),
                        ('name', '=', string),
                        ('view_type', '=', view.type),
                    ], limit=1)
                    if not button_exist:
                        buttons.append({
                                "technical_name": technical_name,
                                "name": string,
                                "type": button_type,
                                "model_id": model_name,
                                "view_type": view.type,
                            })

                if view.type == "kanban":
                    link_nodes = xml_root.xpath("//a[@name]")
                else:
                    link_nodes = []
                for node in link_nodes:
                    technical_name = node.get("name")
                    string = node.get("string") or technical_name
                    button_type = node.get("type")

                    text_content = (node.text or "").strip()
                    text_content = node.xpath("string(.)").strip()

                    if not technical_name:
                        continue

                    if technical_name == string :
                        text_value = text_content if text_content else technical_name
                    else :
                        text_value = string

                    existing = self.sudo().search([
                        ("model_access_id", "=", access_model_id),
                        ("technical_name", "=", technical_name),
                        ("type", "=", button_type),
                        ("name", "=", text_value),
                        ("view_type", "=", view.type),
                    ], limit=1)

                    if not existing:
                        buttons.append({
                            "technical_name": technical_name,
                            "name": text_value,
                            "type": button_type,
                            "model_id": model_name,
                            "view_type": view.type,
                        })

            except Exception as e:
                _logger.error("Error parsing XML for view %s: %s", view.id, e)

        seen = set()
        unique_buttons = []
        for b in buttons:
            key = (b["technical_name"], b["name"], b["view_type"])
            if key not in seen:
                seen.add(key)
                unique_buttons.append(b)
        return unique_buttons


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    user_ids = fields.Many2many('res.users', string="Restricted Users",)

    @api.returns('self')
    def _filter_visible_menus(self):
        menus = super()._filter_visible_menus()
        return menus.filtered( lambda m: self.env.user not in m.user_ids)


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = "res.config.settings"

    hide_chatter_section = fields.Boolean("Hide Chatter Section", default=False)
    hide_send_mssge = fields.Boolean("Hide Send Message Button" , default=False)
    hide_log_note = fields.Boolean("Hide Log Note Button", default=False)
    hide_activities = fields.Boolean("Hide Activities Button", default=False)
    hide_attachment = fields.Boolean("Hide Attachment Button", default=False)
    hide_chatter_edit = fields.Boolean("Hide Chatter Edit Option", default=False)
    hide_chatter_delete = fields.Boolean("Hide Chatter Delete Option", default=False)

    show_import = fields.Boolean("Hide Upload Option", default=False)
    is_export = fields.Boolean("Hide Export Option", default=False)
    is_import = fields.Boolean("Hide Import Option", default=False)
    is_addProperty = fields.Boolean("Hide Add a Properties",  default=False)
    is_archive = fields.Boolean("Hide Archive/UnArchive",default=False)
    is_duplicate = fields.Boolean("Hide Duplicate", default=False)

    def set_values(self):
        res = super(ResConfigSettingsInherit, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.hide_chatter_section', self.hide_chatter_section)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.hide_send_mssge', self.hide_send_mssge)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.hide_log_note', self.hide_log_note)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.hide_activities', self.hide_activities)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.hide_attachment', self.hide_attachment)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.hide_chatter_edit', self.hide_chatter_edit)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.hide_chatter_delete', self.hide_chatter_delete)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.show_import', self.show_import)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.is_export', self.is_export)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.is_addProperty', self.is_addProperty)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.is_archive', self.is_archive)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.is_duplicate', self.is_duplicate)
        self.env['ir.config_parameter'].sudo().set_param('custom_model_access_management.is_import', self.is_import)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsInherit, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            hide_chatter_section=params.get_param('custom_model_access_management.hide_chatter_section'),
            hide_send_mssge=params.get_param('custom_model_access_management.hide_send_mssge'),
            hide_log_note=params.get_param('custom_model_access_management.hide_log_note'),
            hide_activities=params.get_param('custom_model_access_management.hide_activities'),
            hide_attachment=params.get_param('custom_model_access_management.hide_attachment'),
            hide_chatter_edit=params.get_param('custom_model_access_management.hide_chatter_edit'),
            hide_chatter_delete=params.get_param('custom_model_access_management.hide_chatter_delete'),
            show_import=params.get_param('custom_model_access_management.show_import'),
            is_export=params.get_param('custom_model_access_management.is_export'),
            is_addProperty=params.get_param('custom_model_access_management.is_addProperty'),
            is_archive=params.get_param('custom_model_access_management.is_archive'),
            is_duplicate=params.get_param('custom_model_access_management.is_duplicate'),
            is_import=params.get_param('custom_model_access_management.is_import'),
        )
        return res

