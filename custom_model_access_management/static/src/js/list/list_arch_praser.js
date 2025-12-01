/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListArchParser } from "@web/views/list/list_arch_parser";
import { rpc } from "@web/core/network/rpc";

import { syncFetchModelAccess, syncFetchButtons } from "../model_access_utils";

const originalListArchParser = ListArchParser.prototype.parse;

patch(ListArchParser.prototype, {
     parse (xmlDoc, models, modelName) {
        const originalparse =  originalListArchParser.call(this, xmlDoc, models, modelName);
        const buttons = syncFetchButtons(modelName);
        const RemoveButtons = Array.isArray(buttons) ? buttons : [];
        if (RemoveButtons.length > 0 ) {
            originalparse.headerButtons  = originalparse.headerButtons.filter(
                    (item) => !RemoveButtons.includes(item.clickParams['name'])
            );
        }
        originalparse['RemoveButtons'] = RemoveButtons;
        originalparse['custom_active_Action'] = syncFetchModelAccess(modelName);
        return originalparse
     },
});

