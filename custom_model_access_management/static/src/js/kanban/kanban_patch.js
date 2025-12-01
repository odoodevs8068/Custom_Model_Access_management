/** @odoo-module */
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { KanbanArchParser } from "@web/views/kanban/kanban_arch_parser";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
const { onWillStart, onMounted, useRef } = owl;
import { syncFetchModelAccess, syncFetchButtons } from "../model_access_utils";

const originalKanbanArchParser = KanbanArchParser.prototype.parse;
patch(KanbanArchParser.prototype, {
    parse(xmlDoc, models, modelName) {
        this.custom_active_Action = syncFetchModelAccess(modelName);
        const buttons = syncFetchButtons(modelName);
        this.removeList = Array.isArray(buttons) ? buttons : [];

        const buttonTags = xmlDoc.querySelectorAll("button[name], a[name]");
        buttonTags.forEach(btn => {
            if (btn.getAttribute("name") && btn.tagName === 'button') {
                if (this.removeList.includes(btn.getAttribute("name"))) {
                    btn.remove();
                }
            }
        });

        const menu = xmlDoc.querySelector("templates t[t-name='menu']");
        if (menu) {
            const anchors = menu.querySelectorAll("a[name]");
            anchors.forEach(a => {
                const name = a.getAttribute("name");
                if (this.removeList.includes(name)) {
                    a.remove();
                }
            });
        }
        const card = xmlDoc.querySelector("templates t[t-name='card']");
        if (card) {
            const anchors = card.querySelectorAll("a[name]");
            anchors.forEach(a => {
                const name = a.getAttribute("name");
                if (this.removeList.includes(name)) {
                    a.setAttribute("style", "display:none !important;");
                }
            });
        }

        const result =  originalKanbanArchParser.call(this, xmlDoc, models, modelName);
        result['custom_active_Action'] = this.custom_active_Action
        return result;
    },
});

patch(KanbanRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");

        this.custom_active_Action =  this.props.archInfo.custom_active_Action;
        if (this.custom_active_Action) {
            if (this.custom_active_Action.is_create) {
                this.props.archInfo.activeActions.create = false;
                this.props.archInfo.activeActions.createGroup = false;
                this.props.archInfo.activeActions.quickCreate = false;
                this.props.canQuickCreate = false;
            }
            if (this.custom_active_Action.is_delete) {
                this.props.archInfo.activeActions.delete = false;
                this.props.archInfo.activeActions.deleteGroup = false;
            }
            if (this.custom_active_Action.is_edit) {
                this.props.archInfo.activeActions.edit = false;
                this.props.archInfo.activeActions.editGroup = false;
                this.props.archInfo.recordsDraggable = false;
            }
            if (this.custom_active_Action.is_duplicate) {
                this.props.archInfo.activeActions.duplicate = false;
            }
            if (this.custom_active_Action.is_archive) {
                this.props.archInfo.activeActions.archiveGroup = false;
            }
            if (this.custom_active_Action.is_import) { this.env.config.viewArch.setAttribute("import", 0) ; }
            else { this.env.config.viewArch.setAttribute("import", 1); }
        }

    },


});
