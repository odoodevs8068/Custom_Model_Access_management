/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
const { onWillStart, onMounted, useRef } = owl;

import { registry } from "@web/core/registry";
const fileUploadListView = registry.category("views");

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
        this.env.config['custom_active_Action'] = this.archInfo.custom_active_Action;
        if (this.archInfo.custom_active_Action) {
            if (this.archInfo.custom_active_Action.is_create) this.activeActions.create = false;
            if (this.archInfo.custom_active_Action.is_edit) this.activeActions.edit = false;
            if (this.archInfo.custom_active_Action.is_delete) this.activeActions.delete = false;
            if (this.archInfo.custom_active_Action.is_duplicate) this.activeActions.duplicate = false;
            if (this.archInfo.custom_active_Action.is_archive) this.archiveEnabled = false;

            if (this.archInfo.custom_active_Action.is_export) {
                this.env.config.viewArch.setAttribute("export_xlsx", 0);
            }

            if (this.archInfo.custom_active_Action.is_import) { this.env.config.viewArch.setAttribute("import", 0) ; }
            else { this.env.config.viewArch.setAttribute("import", 1); }

            onMounted(() => {
                setTimeout(() => this.SetExportEnable(), 100);
            });
        }
    },

    SetExportEnable() {
         if (this.archInfo?.custom_active_Action?.is_export) this.isExportEnable = false;
    }
});
