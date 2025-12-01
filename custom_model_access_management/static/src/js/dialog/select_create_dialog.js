/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";
import { onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { syncFetchModelAccess } from "../model_access_utils";

patch(SelectCreateDialog.prototype, {
     setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.actionService = useService("action");
        const user_id = this.props.context.uid;
        const model = this.props.resModel;
        this.custom_active_Action = syncFetchModelAccess(model);
        if (this.custom_active_Action) {
            if (this.custom_active_Action.is_create) this.props.noCreate = true;
        }
     }

});





