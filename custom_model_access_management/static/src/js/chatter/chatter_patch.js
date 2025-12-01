/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { Chatter } from "@mail/chatter/web_portal/chatter";
import {  Component, toRaw , onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { Composer } from "@mail/core/common/composer";
import { syncFetchModelAccess } from "../model_access_utils";
import { MessageConfirmDialog } from "@mail/core/common/message_confirm_dialog";

const messageActionsRegistry = registry.category("mail.message/actions");

function wrapCondition(action_id, hide_checker) {
    const action = messageActionsRegistry.get(action_id);
    const original = action.condition;
    patch(action, {
        condition(component) {
            try {
                const model = component?.props?.message?.model;
                const access = syncFetchModelAccess(model);

                if (access && hide_checker(access)) {
                    return false;
                }
            } catch (e) {
                console.warn("ChatterAccess condition error:", e);
            }
            return original(component);
        },
    });
}

patch(Chatter.prototype, {
     setup() {
        super.setup(...arguments);

        this.props.hide_chatter_section = false;
        this.props.hide_send_mssge = false;
        this.props.hide_log_note = false;
        this.props.hide_attachment = false;
        this.props.hide_chatter_edit = false;
        this.props.hide_chatter_delete = false;

        this.orm = useService("orm");
        this.actionService = useService("action");

        const user_id = this.env?.model?.config?.context?.uid || '';
        const model = this.props?.threadModel || this.env?.model?.config?.resModel;
        const ChatterAccess = syncFetchModelAccess(model);
        if (ChatterAccess) {
            if (ChatterAccess.hide_chatter_section) this.props.hide_chatter_section = true;
            if (ChatterAccess.hide_send_mssge) this.props.hide_send_mssge = true;
            if (ChatterAccess.hide_log_note) this.props.hide_log_note = true;
            if (ChatterAccess.hide_attachment) this.props.hide_attachment = true;
            if (ChatterAccess.hide_activities) this.props.has_activities = false;
            wrapCondition("edit", (access) => access.hide_chatter_edit);
            wrapCondition("delete", (access) => access.hide_chatter_delete);
        }
     }
});

patch(Composer.prototype, {
     setup() {
        super.setup(...arguments);
        const CurrentThreadModel = this.thread?.model || this.env?.message?.model ;
        this.ChatterAccess = syncFetchModelAccess(CurrentThreadModel);
        if (this.ChatterAccess && this.ChatterAccess.hide_send_mssge) {
                this.props.showFullComposer = false;
        }
     },

     async sendMessage() {
        if (this.ChatterAccess.hide_send_mssge) {
            return;
        }
        const composer = toRaw(this.props.composer);
        if (composer.message) {
            this.editMessage();
            return;
        }
        await this.processMessage(async (value) => {
            await this._sendMessage(value, this.postData, this.extraData);
        });
     },

     async editMessage() {
        const composer = toRaw(this.props.composer);
        if (composer.text || composer.message.attachment_ids.length > 0) {
            await this.processMessage(async (value) =>
                composer.message.edit(value, composer.attachments, {
                    mentionedChannels: composer.mentionedChannels,
                    mentionedPartners: composer.mentionedPartners,
                })
            );
        }
        this.suggestion?.clearRawMentions();
     }
});
