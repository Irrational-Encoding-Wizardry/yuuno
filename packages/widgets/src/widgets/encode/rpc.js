"use strict";
exports.__esModule = true;
exports.getRPCForModel = void 0;
var rpc_1 = require("../../rpc");
var model_rpc_1 = require("../../model-rpc");
function getRPCForModel(model) {
    var channel = new model_rpc_1.WidgetChannel(model);
    return new rpc_1.RPCClient(channel).makeProxy((0, rpc_1.timeout)(10000));
}
exports.getRPCForModel = getRPCForModel;
