/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { Many2XAutocomplete ,  useActiveActions } from "@web/views/fields/relational_utils";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";

import { syncFetchModelAccess } from "../model_access_utils";

patch(Many2XAutocomplete.prototype, {
    setup() {
        super.setup(...arguments);
        const orm = useService("orm");
        const user = this.props.context.uid;
        const model = this.props.resModel;

        this.custom_active_Action = syncFetchModelAccess(model);
        if (this.custom_active_Action.is_create) {
                 this.props.activeActions.create = false;
                 this.props.activeActions.createEdit = false;
                 this.props.activeActions.write = false;
                 this.props.quickCreate = null;
        }
        if (this.custom_active_Action.is_edit) this.props.activeActions.write = false;

    },

    async loadOptionsSource(request) {
        if (this.custom_active_Action === undefined) {
            await onWillStart(() => {});
        }
        const options = await super.loadOptionsSource(request);
        if (this.custom_active_Action && this.custom_active_Action.is_create === true) {
            const filtered = options.filter((o) => {
                const classes = o.classList?.split(" ") || [];
                const isCreateOption =
                    classes.includes("o_m2o_dropdown_option_create") ||
                    o.action === "quick_create" ||
                    o.action === "create" ||
                    o.dataset?.action === "quick_create" ||
                    o.dataset?.action === "create";

                return !isCreateOption;
            });
            return filtered;
        }
        return options;
    }

});

