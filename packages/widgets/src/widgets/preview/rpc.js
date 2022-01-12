"use strict";
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
exports.__esModule = true;
exports.getRPCForModel = void 0;
var rpc_1 = require("../../rpc");
var model_rpc_1 = require("../../model-rpc");
var CachedPreviewRPC = /** @class */ (function () {
    function CachedPreviewRPC(parent, model) {
        this._cache = new Map();
        this._lru = [];
        this.parent = parent;
        this.model = model;
    }
    CachedPreviewRPC.prototype.clear = function () {
        this._cache.clear();
    };
    CachedPreviewRPC.prototype.open = function () {
        this.parent.open();
    };
    CachedPreviewRPC.prototype.close = function () {
        this.parent.close();
    };
    CachedPreviewRPC.prototype.length = function () {
        return this.parent.length();
    };
    CachedPreviewRPC.prototype.frame = function (_a) {
        var frame = _a.frame, image = _a.image;
        if (!image)
            image = "clip";
        var realId = this.model.get("clips")[this.model.get(image)];
        var _lru_id = "".concat(realId, "--").concat(image, "--").concat(frame);
        if (!this._cache.has(_lru_id)) {
            this._evict();
            this._cache.set(_lru_id, this.parent.frame({ frame: frame, image: image }));
        }
        this._hit(_lru_id);
        return this._cache.get(_lru_id);
    };
    CachedPreviewRPC.prototype._hit = function (id) {
        if (this._lru.indexOf(id) == 0)
            return;
        this._lru = __spreadArray([id], this._lru.filter(function (f) { return f != id; }), true);
    };
    CachedPreviewRPC.prototype._evict = function () {
        if (this._lru.length <= 10)
            return;
        var evicted = this._lru.pop();
        this._cache["delete"](evicted);
    };
    return CachedPreviewRPC;
}());
function getRPCForModel(model) {
    var channel = new model_rpc_1.WidgetChannel(model);
    return new CachedPreviewRPC(new rpc_1.RPCClient(channel).makeProxy((0, rpc_1.timeout)(10000)), model);
}
exports.getRPCForModel = getRPCForModel;
