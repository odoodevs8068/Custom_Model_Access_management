from odoo.addons.web.controllers.export import Export
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception
import json


class CustomExport(Export):

    @http.route('/web/export/get_fields', type='json', auth="user")
    def get_fields(
        self, model, domain, prefix='', parent_name='', import_compat=True,
        parent_field_type=None, parent_field=None, exclude=None
    ):
        records = super().get_fields(
            model, domain, prefix, parent_name, import_compat,
            parent_field_type, parent_field, exclude
        )

        records = self.remove_restricted_fields(records)
        filtered_records = self.remove_user_hide_fields(records, model)
        return filtered_records

    def remove_restricted_fields(self, records):
        filtered_records = []
        check_access = request.env['model_access.right'].sudo().search([('type', '=', 'show_field')])
        if check_access:
            for rec in records:
                allow = True
                for rule in check_access:
                    if rule.field_id.name and rule.field_id.name == rec['id']:
                        if rule.user_ids and request.env.uid not in rule.user_ids.ids:
                            allow = False
                            break
                    elif rule.field_id.name and f"/{rule.field_id.name}" in rec['id']:
                        if rule.user_ids and request.env.uid not in rule.user_ids.ids:
                            allow = False
                            break
                if allow:
                    filtered_records.append(rec)
        else:
            filtered_records = records
        return filtered_records

    def remove_user_hide_fields(self, records, model):
        check_access = request.env['model_access.right'].sudo().search([
            ('user_id', '=', request.env.user.id),
            ('model_id.model', '=', model),
            ('export_fields_ids', '!=', False)
        ])
        if not check_access:
            return records
        fields_to_hide = set()
        for rule in check_access:
            fields_to_hide.update(rule.export_fields_ids.mapped('name'))
        filtered_records = []
        for rec in records:
            field_name = rec.get('id', '').split('/')[-1]
            if field_name in fields_to_hide:
                continue
            filtered_records.append(rec)
        return filtered_records


class HiddenButtonsController(http.Controller):

    @http.route('/header/buttons', type='http', auth='user', csrf=False)
    def get_hidden_header_buttons(self, **kw):
        import json
        raw_data = request.httprequest.get_data()
        data = json.loads(raw_data.decode('utf-8'))
        params = data.get("params", {})
        model_name = params.get("model_name")
        result = request.env["model_access.right"].sudo().get_hidden_header_buttons(model_name)
        return json.dumps({"result": result})

    @http.route('/custom_model_access', type='http', auth='user', csrf=False)
    def get_custom_model_access(self, **kw):
        raw_data = request.httprequest.get_data()
        data = json.loads(raw_data.decode('utf-8'))
        params = data.get("params", {})
        model_name = params.get("model_name")
        result = request.env["model_access.right"].sudo().get_bulk_access(model_name)
        return json.dumps({"result": result})

    @http.route('/hide_templates', type='json', auth='user', readonly=True)
    def hide_templates(self, model_name):
        if not model_name:
            return []
        try:
            result = request.env['model_access.right'].sudo().get_hide_templates(model_name)
        except Exception:
            result = []
        return result


