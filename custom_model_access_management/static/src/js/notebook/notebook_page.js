/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { Notebook } from "@web/core/notebook/notebook";
import {  Component, toRaw , onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


const OriginalComputePages = Notebook.prototype.computePages

patch(Notebook.prototype, {
     setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.actionService = useService("action");

        const user_id = this.env?.model?.config?.context?.uid || '';
        const model = this.env?.model?.config?.resModel  || this.env?.env?.searchModel?.resModel;

        onWillStart(async () => {
            try {
                this.NotebookPageAccess = await this.orm.call( "model_access.right", "get_form_notebook_page", [model]  );
            } catch (error) {
                console.warn('Failed to load access rights:', error);
            }
         });
     },

     computePages(props) {
        const originalPages = OriginalComputePages.call(this, props);
        if (this.NotebookPageAccess?.length) {
            for (const [, page] of originalPages) {
                if (page.title && this.NotebookPageAccess.includes(page.title)) {
                    page.isVisible = false;
                }
            }
        }
        return originalPages;
    },

});