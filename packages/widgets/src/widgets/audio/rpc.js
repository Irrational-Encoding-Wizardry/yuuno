"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
exports.__esModule = true;
exports.AudioSource = void 0;
var rpc_1 = require("../../rpc");
var model_rpc_1 = require("../../model-rpc");
var AudioSource = /** @class */ (function () {
    function AudioSource(model) {
        this._open = false;
        this._channels = 0;
        this._frames = 0;
        this._loaded = 0;
        this._samples = 0;
        this._sample_rate = 0;
        this.ondata = function () { };
        this.rpc = new rpc_1.RPCClient(new model_rpc_1.WidgetChannel(model)).makeProxy((0, rpc_1.timeout)(10000));
    }
    AudioSource.prototype.open = function () {
        this.rpc.open();
        this._open = true;
    };
    AudioSource.prototype.close = function () {
        this._open = false;
        this.rpc.close();
    };
    Object.defineProperty(AudioSource.prototype, "channels", {
        get: function () {
            return this._channels;
        },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(AudioSource.prototype, "loaded", {
        get: function () {
            return this._loaded;
        },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(AudioSource.prototype, "samples", {
        get: function () {
            return this._samples;
        },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(AudioSource.prototype, "sample_rate", {
        get: function () {
            return this._sample_rate;
        },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(AudioSource.prototype, "frames", {
        get: function () {
            return this._frames;
        },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(AudioSource.prototype, "duration", {
        get: function () {
            return this._samples / this._sample_rate;
        },
        enumerable: false,
        configurable: true
    });
    AudioSource.prototype.loadMetadata = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _a, frames_1, channel_count, samples_per_second, sample_count;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        if (!(this._frames === 0)) return [3 /*break*/, 2];
                        return [4 /*yield*/, this.rpc.meta()];
                    case 1:
                        _a = _b.sent(), frames_1 = _a.frames, channel_count = _a.channel_count, samples_per_second = _a.samples_per_second, sample_count = _a.sample_count;
                        this._frames = frames_1;
                        this._sample_rate = samples_per_second;
                        this._samples = sample_count;
                        this._channels = channel_count;
                        _b.label = 2;
                    case 2:
                        this.ondata();
                        return [2 /*return*/];
                }
            });
        });
    };
    AudioSource.prototype.render = function (start, received) {
        return __awaiter(this, void 0, void 0, function () {
            var frame, _a, size, buffers;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        if (!(this._frames === 0)) return [3 /*break*/, 2];
                        return [4 /*yield*/, this.loadMetadata()];
                    case 1:
                        _b.sent();
                        _b.label = 2;
                    case 2:
                        frame = start;
                        _b.label = 3;
                    case 3:
                        if (!(frame < this._frames)) return [3 /*break*/, 6];
                        if (!this._open)
                            return [3 /*break*/, 6];
                        return [4 /*yield*/, this.rpc.render({ frame: frame })];
                    case 4:
                        _a = _b.sent(), size = _a.size, buffers = _a.buffers;
                        this._loaded += size;
                        if (!received(frame, size, buffers))
                            return [3 /*break*/, 6];
                        _b.label = 5;
                    case 5:
                        frame++;
                        return [3 /*break*/, 3];
                    case 6: return [2 /*return*/];
                }
            });
        });
    };
    return AudioSource;
}());
exports.AudioSource = AudioSource;
