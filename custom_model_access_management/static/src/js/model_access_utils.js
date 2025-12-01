/** @odoo-module **/

export function syncFetchButtons(model) {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/header/buttons", false);
    xhr.setRequestHeader("Content-Type", "application/json");

    const body = JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: { model_name: model },
        id: Date.now(),
    });

    xhr.send(body);

    try {
        const resp = JSON.parse(xhr.responseText);
        return resp.result || [];
    } catch {
        return [];
    }
}


const MODEL_ACCESS_CACHE = {};
export function syncFetchModelAccess(model) {

    if (MODEL_ACCESS_CACHE[model]) {
        return MODEL_ACCESS_CACHE[model];
    }

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/custom_model_access", false);
    xhr.setRequestHeader("Content-Type", "application/json");

    const body = JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: { model_name: model },
        id: Date.now(),
    });

    try {
        xhr.send(body);
        const resp = JSON.parse(xhr.responseText);
        const result = resp.result || {};

        MODEL_ACCESS_CACHE[model] = result;
        return result;

    } catch (e) {
        console.error("Model Access Fetch Failed:", e);
        return {};
    }
}




//export function syncFetchModelAccess(model) {
//    const xhr = new XMLHttpRequest();
//    xhr.open("POST", "/custom_model_access", false);
//    xhr.setRequestHeader("Content-Type", "application/json");
//
//    const body = JSON.stringify({
//        jsonrpc: "2.0",
//        method: "call",
//        params: { model_name: model },
//        id: Date.now(),
//    });
//
//    xhr.send(body);
//
//    try {
//        const resp = JSON.parse(xhr.responseText);
//        return resp.result || [];
//    } catch {
//        return [];
//    }
//}
