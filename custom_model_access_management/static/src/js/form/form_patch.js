/** @odoo-module */
import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
const { onWillStart, onMounted, useRef } = owl;


patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.custom_access = this.archInfo.custom_active_action;
        if (this.custom_access) {
            if (this.custom_access.is_create) this.archInfo.activeActions.create = false;
            if (this.custom_access.is_create) this.canCreate = false;
            if (this.custom_access.is_edit) this.archInfo.activeActions.edit = false;
            if (this.custom_access.is_edit) this.archInfo.activeActions.canEdit = false;
            if (this.custom_access.is_delete) this.archInfo.activeActions.delete = false;
            if (this.custom_access.is_duplicate) this.archInfo.activeActions.duplicate = false;
            if (this.custom_access.is_addProperty) this.archInfo.activeActions.addPropertyFieldValue = false;
             if (this.custom_access.is_archive) {
                Object.defineProperty(this, "archiveEnabled", {
                        get() { return false; },
                    });
            }
        }

        onMounted(() => {
            if (this.custom_access && this.custom_access.hide_chatter_section === true ) {
                const form_sheet_bg = document.querySelector(".o_form_sheet_bg");
                if (form_sheet_bg && (this.custom_access.o_attachment_preview === true && this.custom_access.remove_attachment_preview === true )) {
                    form_sheet_bg.setAttribute("style", "min-width: fit-content !important;");
                }
            }
        });
    },

});