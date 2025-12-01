/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { View } from "@web/views/view";
import { onWillStart } from "@odoo/owl";

patch(View.prototype, {
     setup() {
        super.setup(...arguments);
     }

});