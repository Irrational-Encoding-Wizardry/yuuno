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
exports.AudioPlayer = void 0;
var COMBINED_FRAMES = 24;
var SAMPLES_PER_VS_FRAME = 3072;
var SAMPLES_PER_REQUEST = COMBINED_FRAMES * SAMPLES_PER_VS_FRAME;
// How many seconds should be loaded before
// playback should resume.
var PREFETCH_SECONDS = 5;
// How many seconds can be buffered before we
// pause requesting new chunks every second.
var BUFFER_HIGH_MARK_SECONDS = 30;
// How many seconds should be left before we
// suspend the audio.
var BUFFER_LOW_MARK_SECONDS = 2;
function calculatePosition(sample) {
    var frame = Math.floor(sample / SAMPLES_PER_REQUEST);
    var offset = sample % SAMPLES_PER_REQUEST;
    return [frame, offset];
}
function clock(tickTime, tick) {
    return __awaiter(this, void 0, void 0, function () {
        var skipped, shouldContinue, _loop_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    skipped = 0;
                    shouldContinue = true;
                    _loop_1 = function () {
                        var start, end, dT;
                        return __generator(this, function (_b) {
                            switch (_b.label) {
                                case 0:
                                    start = new Date().valueOf();
                                    return [4 /*yield*/, tick(skipped)];
                                case 1:
                                    shouldContinue = _b.sent();
                                    end = new Date().valueOf();
                                    dT = end - start;
                                    if (!(dT < tickTime)) return [3 /*break*/, 3];
                                    skipped = 0;
                                    if (tickTime - dT < 100)
                                        return [2 /*return*/, "continue"]; // Increase stability by skipping timeout on short times.
                                    return [4 /*yield*/, new Promise(function (rs) { return setTimeout(rs, tickTime - dT); })];
                                case 2:
                                    _b.sent();
                                    return [3 /*break*/, 4];
                                case 3:
                                    skipped = Math.ceil(tickTime / dT);
                                    _b.label = 4;
                                case 4: return [2 /*return*/];
                            }
                        });
                    };
                    _a.label = 1;
                case 1: return [5 /*yield**/, _loop_1()];
                case 2:
                    _a.sent();
                    _a.label = 3;
                case 3:
                    if (shouldContinue) return [3 /*break*/, 1];
                    _a.label = 4;
                case 4: return [2 /*return*/];
            }
        });
    });
}
function microtask(func) {
    new Promise(function (rs) { return rs(); }).then(function () { return func(); });
}
var AudioPlayer = /** @class */ (function () {
    function AudioPlayer(source) {
        this._paused = true;
        this._onpause = null;
        this.ontick = function () { };
        this.source = source;
    }
    Object.defineProperty(AudioPlayer.prototype, "playable", {
        get: function () {
            return this._onpause === null;
        },
        enumerable: false,
        configurable: true
    });
    AudioPlayer.prototype.play = function (startAt) {
        if (startAt === void 0) { startAt = 0; }
        return __awaiter(this, void 0, void 0, function () {
            var ctx, _a, nextFrame, currentOffset, currentSecond, startSecond, maxLength, lastCurrentTime, lastBuffers;
            var _this = this;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        if (!this._paused)
                            return [2 /*return*/];
                        if (this._onpause !== null)
                            return [2 /*return*/];
                        this._paused = false;
                        // Ensure we have a full integer start at.
                        startAt = Math.floor(startAt);
                        // Make sure the metadata is loaded.
                        return [4 /*yield*/, this.source.loadMetadata()];
                    case 1:
                        // Make sure the metadata is loaded.
                        _b.sent();
                        ctx = new AudioContext();
                        return [4 /*yield*/, ctx.suspend()];
                    case 2:
                        _b.sent();
                        // Register the neccessary callbacks.
                        this._onpause = function () { return ctx.suspend(); };
                        _a = calculatePosition(startAt), nextFrame = _a[0], currentOffset = _a[1];
                        currentSecond = 0;
                        startSecond = startAt / this.source.sample_rate;
                        maxLength = (this.source.samples - startAt) / this.source.sample_rate;
                        lastCurrentTime = 0;
                        clock(500, function () { return __awaiter(_this, void 0, void 0, function () {
                            var event;
                            var _this = this;
                            return __generator(this, function (_a) {
                                if (ctx.state !== "closed")
                                    lastCurrentTime = ctx.currentTime;
                                event = {
                                    currentTime: Math.min(lastCurrentTime, maxLength) + startSecond,
                                    bufferSecond: Math.min(currentSecond, maxLength) + startSecond,
                                    playing: !this._paused
                                };
                                microtask(function () {
                                    _this.ontick(event);
                                });
                                return [2 /*return*/, !this._paused];
                            });
                        }); })["catch"](console.error);
                        if (!(SAMPLES_PER_REQUEST - currentOffset > this.source.sample_rate)) return [3 /*break*/, 3];
                        //   1. >1 second left at the sample to start:
                        //      Make the offset negative to cause the initial buffer to
                        //      take from beyond the start of b2 below.
                        //
                        //             <OFFSET>
                        //      SECOND         |----------------|
                        //      BUFFER |-----------------------------|:-----....
                        //
                        //      or before:
                        lastBuffers = new Array(this.source.channels);
                        lastBuffers.fill(new ArrayBuffer(SAMPLES_PER_REQUEST * 4));
                        currentOffset *= -1;
                        return [3 /*break*/, 5];
                    case 3: 
                    //   2. <1 second left:
                    //      Prefetch the buffer and set it as the last buffer.
                    //                              <-- OFFSET -->
                    //      SECOND                  |----------------|
                    //      BUFFER |-----------------------------|:-----....
                    return [4 /*yield*/, this.source.render(nextFrame, function (_, __, buffers) {
                            lastBuffers = buffers;
                            return false;
                        })];
                    case 4:
                        //   2. <1 second left:
                        //      Prefetch the buffer and set it as the last buffer.
                        //                              <-- OFFSET -->
                        //      SECOND                  |----------------|
                        //      BUFFER |-----------------------------|:-----....
                        _b.sent();
                        nextFrame++;
                        currentOffset = SAMPLES_PER_REQUEST - currentOffset;
                        _b.label = 5;
                    case 5:
                        _b.trys.push([5, , 7, 8]);
                        return [4 /*yield*/, clock(1000, function (skipped) { return __awaiter(_this, void 0, void 0, function () {
                                var _this = this;
                                return __generator(this, function (_a) {
                                    switch (_a.label) {
                                        case 0:
                                            if (this._paused)
                                                return [2 /*return*/, false];
                                            // If we finished rendering the node, play to the end.
                                            if (nextFrame >= this.source.frames) {
                                                return [2 /*return*/, currentSecond >= ctx.currentTime];
                                            }
                                            // Stop rendering after having buffered for 30 seconds and we did not skip any ticks.
                                            if (skipped == 0 && currentSecond - ctx.currentTime > BUFFER_HIGH_MARK_SECONDS)
                                                return [2 /*return*/, true];
                                            // All other cases: Process additional frames
                                            return [4 /*yield*/, this.source.render(nextFrame, function (frameNo, _, buffers) {
                                                    // Bail on pausing.
                                                    if (_this._paused)
                                                        return false;
                                                    if (currentSecond - ctx.currentTime < BUFFER_LOW_MARK_SECONDS) {
                                                        ctx.suspend();
                                                    }
                                                    // Advance the frame counter.
                                                    nextFrame = frameNo + 1;
                                                    // Build the AudioBuffer instances that we can construct.
                                                    // All of them are for exactly one full second.
                                                    var result = buildBuffer(_this.source, lastBuffers, buffers, currentOffset, _this.source.sample_rate);
                                                    currentOffset = result[1];
                                                    lastBuffers = buffers;
                                                    // Queue the samples.
                                                    for (var _i = 0, _a = result[0]; _i < _a.length; _i++) {
                                                        var audio = _a[_i];
                                                        var node = new AudioBufferSourceNode(ctx, { buffer: audio });
                                                        node.connect(ctx.destination);
                                                        node.start(currentSecond++);
                                                    }
                                                    // Stop fetching additional chunks if we step over prefetch.
                                                    return currentSecond - ctx.currentTime < PREFETCH_SECONDS;
                                                })];
                                        case 1:
                                            // All other cases: Process additional frames
                                            _a.sent();
                                            if (!(ctx.state === "suspended" && !this._paused)) return [3 /*break*/, 3];
                                            return [4 /*yield*/, ctx.resume()];
                                        case 2:
                                            _a.sent();
                                            _a.label = 3;
                                        case 3: return [2 /*return*/, !this._paused];
                                    }
                                });
                            }); })];
                    case 6:
                        _b.sent();
                        return [3 /*break*/, 8];
                    case 7:
                        ctx.close();
                        this._onpause = null;
                        this._paused = true;
                        return [7 /*endfinally*/];
                    case 8: return [2 /*return*/];
                }
            });
        });
    };
    AudioPlayer.prototype.pause = function () {
        if (!!this._onpause)
            this._onpause();
        this._paused = true;
    };
    AudioPlayer.prototype.open = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        this.source.open();
                        return [4 /*yield*/, this.source.loadMetadata()];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    return AudioPlayer;
}());
exports.AudioPlayer = AudioPlayer;
function buildBuffer(source, buffer1, buffer2, offset, length) {
    var b1 = buffer1[0].byteLength / 4;
    var b2 = buffer2[0].byteLength / 4;
    var lb = length - offset;
    var rest = b2 - lb;
    var result = [];
    if (offset >= 0) {
        var buffer = new AudioBuffer({
            length: length,
            sampleRate: source.sample_rate,
            numberOfChannels: source.channels
        });
        result.push(buffer);
        if (offset > 0) {
            copyFromBuffers(buffer, buffer1, b1 - offset, 0);
        }
        copyFromBuffers(buffer, buffer2, 0, offset);
    }
    while (rest > length) {
        var buffer = new AudioBuffer({
            length: length,
            sampleRate: source.sample_rate,
            numberOfChannels: source.channels
        });
        result.push(buffer);
        copyFromBuffers(buffer, buffer2, b2 - rest, 0);
        rest -= length;
    }
    return [result, rest];
}
function copyFromBuffers(buffer, channels, channelOffset, startOffset) {
    for (var channel = 0; channel < channels.length; channel++) {
        buffer.copyToChannel(new Float32Array(channels[channel], channelOffset * 4), channel, startOffset);
    }
}
