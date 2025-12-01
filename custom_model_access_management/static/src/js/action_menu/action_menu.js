/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ActionMenus } from "@web/search/action_menus/action_menus";

const originalGetActionItems = ActionMenus.prototype.getActionItems;
const originalLoadPrintItems = ActionMenus.prototype.loadPrintItems;

patch(ActionMenus.prototype, {

     setup() {
        super.setup(...arguments);
        this.currentModel = this.env.model?.root?.resModel || this.env.model?.resModel || "unknown";
     },

    async getActionItems(props) {
        const resModel =  props.resModel || this.currentModel;
        const originalItems = await originalGetActionItems.call(this, props);
        const access = await this.orm.call( "model_access.right", "get_server_actions", [resModel]  );
        if (access.length > 0 && originalItems.length > 0) {
            const restrictedIds = access;
            const CorrectedActions = originalItems.filter(
                (item) => !restrictedIds.includes(item.key)
            );
           return [...CorrectedActions];
        }
        return [...originalItems];
    },

    async loadPrintItems() {
        const resModel =   this.props.resModel || this.currentModel;
        await originalLoadPrintItems.call(this);
        const access = await this.orm.call( "model_access.right", "get_print_actions", [resModel]  );
        if (access.length > 0) {
            const restrictedIds = access;
            this.state.printItems = this.state.printItems.filter(
                (item) => !restrictedIds.includes(item.key)
            );
        }
    },

});
