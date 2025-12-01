/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormArchParser } from "@web/views/form/form_arch_parser";
import { rpc } from "@web/core/network/rpc";
import { syncFetchModelAccess, syncFetchButtons } from "../model_access_utils";

const originalFormArchParser = FormArchParser.prototype.parse;


patch(FormArchParser.prototype, {
     parse(xmlDoc, models, modelName) {
        this.custom_active_action = syncFetchModelAccess(modelName);

        if (this.custom_active_action.remove_attachment_preview) {
            const attachmentDiv = xmlDoc.querySelector('div.o_attachment_preview');
            if (attachmentDiv) {
                attachmentDiv.remove();
            }
        }

        const originalFormparse =  originalFormArchParser.call(this, xmlDoc, models, modelName);
        originalFormparse['custom_active_action'] = this.custom_active_action

        const buttons = syncFetchButtons(modelName);
        const RemoveButtons = Array.isArray(buttons) ? buttons : [];
        const header = xmlDoc.querySelector("header");
        if (header && RemoveButtons && RemoveButtons.length > 0) {
            RemoveButtons.forEach((btnName) => {
                const btns = header.querySelectorAll(`button[name="${btnName}"]`);
                btns.forEach((btn) => {
                    btn.remove();
                });
            });
        }
        return originalFormparse
    },
});
