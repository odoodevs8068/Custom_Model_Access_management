/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ExportDataDialog } from "@web/views/view_dialogs/export_data_dialog";
import { session } from "@web/session";
import { user } from "@web/core/user";
import { rpc } from "@web/core/network/rpc";

const originalFetchFields = ExportDataDialog.prototype.fetchFields;

patch(ExportDataDialog.prototype,  {
    async fetchFields() {
        await originalFetchFields.call(this);
        const CurrentModel = this.props.root._config.resModel || this.props.root.resModel || this.props.root.model.config.resModel
        const HideTemplateIds = await rpc("/hide_templates", {  model_name: CurrentModel});
        this.templates = (this.templates || []).filter((rec) => {
            return !rec.user_ids || rec.user_ids.length === 0 || rec.user_ids.includes(user.userId);
        });
        this.templates = this.templates.filter((rec) => !HideTemplateIds.includes(rec.id));
    },
});
