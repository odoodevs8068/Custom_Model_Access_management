/** @odoo-module */
import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
const { onWillStart, onMounted, useRef } = owl;
import { syncFetchModelAccess } from "../model_access_utils";

import { AddButtonDialog } from "./add_button_dialog";

patch(ListRenderer.prototype, {
    setup() {
        super.setup(...arguments);

        this.orm = useService("orm");
        this.actionService = useService("action");
        this.dialogService = useService("dialog");

        const user_id = this.env.model.config.context.uid;
        const model = this.env.model.config.resModel;

        this.RelationalModelUserAccess = syncFetchModelAccess(this.props?.list?._config?.resModel);

        if (this.props?.archInfo?.custom_active_Action) {
            if (this.props?.archInfo?.custom_active_Action.is_create && this.props.activeActions.type !== "many2many") {
                this.activeActions.create = false;
                this.props.archInfo.creates = [];
                this.props.activeActions.create = false;
                this.creates = [];
            }
        }

        if (this.RelationalModelUserAccess) {
            if (this.RelationalModelUserAccess.is_create && this.props.activeActions.type !== "many2many") {
                this.activeActions.create = false;
                this.props.archInfo.creates = [];
                this.props.activeActions.create = false;
                this.creates = [];
            }
            if (this.RelationalModelUserAccess.is_delete && this.props.activeActions.type !== "many2many") {
                this.props.archInfo.activeActions.delete = false;
                this.props.activeActions.delete = false;
            }
            if (this.RelationalModelUserAccess.is_edit && this.props.activeActions.type !== "many2many") {
                this.props.archInfo.activeActions.edit = false;
                this.props.activeActions.edit = false;
            }
        }

        if (this.props?.list?._config?.resModel === 'model_header_button') {
            this.creates = [];
        }
    },


    async OnAddButtonClick() {
        this.dialogService.add(AddButtonDialog, {
            context: {
                search_model:  'model_access.right',
                model_access_id:  this.env?.model?.config?.resId,
            },
            download: () => {
                console.log("Get Data");
            },
            close: () => {
                console.log("Dialog closed");
            },
        });
    },

    get hasOptionalOpenFormViewColumn() {
        if (this.props?.list?._config?.resModel === "model_access.right") {
            return false;
        }
        return super.hasOptionalOpenFormViewColumn;
    },


});
