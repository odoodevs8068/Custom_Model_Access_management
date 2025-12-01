/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { X2ManyField } from "@web/views/fields/x2many/x2many_field";
import { onWillStart } from "@odoo/owl";
import { syncFetchModelAccess } from "../model_access_utils";


patch(X2ManyField.prototype, {
     setup() {
        super.setup(...arguments);
        const userId = this.props.context.uid
        const model = this.props.record._config.resModel

        this.custom_active_Action = syncFetchModelAccess(model);
        if (this.custom_active_Action.is_create) this.activeActions.create = false;
        if (this.custom_active_Action.is_edit) this.activeActions.edit = false;
        if (this.custom_active_Action.is_delete) this.activeActions.delete = false;

     }

});