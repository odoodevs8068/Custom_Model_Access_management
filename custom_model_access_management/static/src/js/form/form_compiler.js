/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormCompiler } from "@web/views/form/form_compiler";
const { onWillStart, onMounted, useRef , useEnv} = owl;

import { syncFetchButtons } from "../model_access_utils";

const originalViewCompileButton = FormCompiler.prototype.compileButtonBox;

patch(FormCompiler.prototype, {
    setup() {
        const env = useEnv();
        this.modelName = env?.searchModel?.resModel || "unknown_model";
        super.setup(...arguments);
        const buttons = syncFetchButtons(this.modelName);
        this.RemoveButtons = Array.isArray(buttons) ? buttons : [];
     },

    compileButtonBox(el, params) {
        const removeSet = new Set(this.RemoveButtons.map(b => b.toLowerCase()));
        const buttons = Array.from(el.querySelectorAll("button"));
        buttons.forEach((btn) => {
            const name = btn.getAttribute("name");
            if (name && removeSet.has(name.toLowerCase())) {
                btn.remove();
            }
        });
        const result = originalViewCompileButton.call(this, el, params);
        return result;
    },
});

