/** @odoo-module **/
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class AddButtonDialog extends Component {
    static template = "custom_model_access_management.AddButtonDialog";
    static components = { Dialog };
    static props = {
        close: { type: Function },
        context: { type: Object, optional: true },
        download: { type: Function },
    };
    async setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.state = useState({ buttons_data: [] });

        onWillStart(async () => {
            const data  = await this.orm.call( "model_header_button",  "get_button_data", [this.props.context.model_access_id] );
            this.state.buttons_data = data.map((item, index)  => ({
                ...item,
                selected: false,
                 _key: `${item.technical_name}_${item.type}_${item.view_type}_${index}`,
            }));
            this.state.selectAll = false;
        });
    }

    toggleSelectAll(ev) {
        const checked = ev.target.checked;
        this.state.selectAll = checked;
        this.state.buttons_data.forEach(b => {
            b.selected = checked;
        });
    }

    async SelectedRecords() {
        const selected = this.state.buttons_data
            .filter(btn => btn.selected)
            .map(btn => ({
                technical_name: btn.technical_name,
                name: btn.name,
                type: btn.type,
                model_access_id: this.props.context.model_access_id,
                view_type: btn.view_type,
            }));
        if (!selected.length) {
            this.notification.add("No records selected.", { type: "warning" });
            return;
        }
        await this.orm.create("model_header_button", selected);
        this.action.doAction({
            type: "ir.actions.client",
            tag: "reload",
        });
    }

    cancel() {
        this.props.close();
    }
}
