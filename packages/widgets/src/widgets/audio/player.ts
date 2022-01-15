import type { AudioSource } from "./rpc";


const COMBINED_FRAMES = 24;
const SAMPLES_PER_VS_FRAME = 3072;

const SAMPLES_PER_REQUEST = COMBINED_FRAMES * SAMPLES_PER_VS_FRAME;

// How many seconds should be loaded before
// playback should resume.
const PREFETCH_SECONDS = 5;

// How many seconds can be buffered before we
// pause requesting new chunks every second.
const BUFFER_HIGH_MARK_SECONDS = 30;

// How many seconds should be left before we
// suspend the audio.
const BUFFER_LOW_MARK_SECONDS = 2;


function calculatePosition(sample: number): [number, number] {
    const frame = Math.floor(sample / SAMPLES_PER_REQUEST);
    const offset = sample % SAMPLES_PER_REQUEST;

    return [ frame, offset ];
}


async function clock(tickTime: number, tick: (skipped: number) => Promise<boolean>) {
    let skipped = 0;
    let shouldContinue = true;
    do {
        const start = new Date().valueOf();
        shouldContinue = await tick(skipped);
        const end = new Date().valueOf();

        const dT = end - start;
        if (dT < tickTime) {
            skipped = 0;
            if (tickTime - dT < 100) continue;  // Increase stability by skipping timeout on short times.
            await new Promise(rs => setTimeout(rs, tickTime - dT));
        } else {
            skipped = Math.ceil(tickTime / dT);
        }
    } while(shouldContinue);
}


function microtask(func: () => void) {
    new Promise<void>(rs => rs()).then(() => func());
}


export interface PlaybackEvent {
    currentTime: number;
    bufferSecond: number;
    playing: boolean;
}


export class AudioPlayer {
    private source: AudioSource;

    private _paused: boolean = true;
    private _onpause: (() => void)|null = null;

    ontick: (event: PlaybackEvent) => void = () => {};

    constructor(source: AudioSource) {
        this.source = source;
    }

    get playable(): boolean {
        return this._onpause === null;
    }

    async play(startAt: number = 0) {
        if (!this._paused) return;
        if (this._onpause !== null) return;
        this._paused = false;

        // Ensure we have a full integer start at.
        startAt = Math.floor(startAt);

        // Make sure the metadata is loaded.
        await this.source.loadMetadata();

        // Create a new audio context and suspend it until we got the data we need.
        const ctx = new AudioContext();
        await ctx.suspend();

        // Register the neccessary callbacks.
        this._onpause = () => ctx.suspend();

        // Find out where the seeked position starts at.
        let [nextFrame, currentOffset] = calculatePosition(startAt);

        // Calculation for the UI.
        let currentSecond = 0;
        const startSecond = startAt / this.source.sample_rate;
        const maxLength = (this.source.samples - startAt) / this.source.sample_rate;

        // Schedule a callback to inform the UI of the new state.
        let lastCurrentTime = 0;
        clock(500, async () => {
            if (ctx.state !== "closed")
                lastCurrentTime = ctx.currentTime;

            const event = {
                currentTime: Math.min(lastCurrentTime, maxLength) + startSecond,
                bufferSecond: Math.min(currentSecond, maxLength) + startSecond,
                playing: !this._paused
            };
            microtask(() => {
                this.ontick(event)
            });
            return !this._paused;
        }).catch(console.error);


        let lastBuffers: ArrayBuffer[];
        if (SAMPLES_PER_REQUEST - currentOffset > this.source.sample_rate) {
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
            lastBuffers.fill(new ArrayBuffer(SAMPLES_PER_REQUEST*4));
            currentOffset *= -1;
        } else {
            //   2. <1 second left:
            //      Prefetch the buffer and set it as the last buffer.
            //                              <-- OFFSET -->
            //      SECOND                  |----------------|
            //      BUFFER |-----------------------------|:-----....
            await this.source.render(nextFrame, (_, __, buffers) => {
                lastBuffers = buffers;
                return false;
            });
            nextFrame++;
            currentOffset = SAMPLES_PER_REQUEST - currentOffset;
        }

        try {
            await clock(1000, async (skipped) => {
                if (this._paused) return false;

                // If we finished rendering the node, play to the end.
                if (nextFrame >= this.source.frames) {
                    return currentSecond >= ctx.currentTime;
                }

                // Stop rendering after having buffered for 30 seconds and we did not skip any ticks.
                if (skipped == 0 && currentSecond - ctx.currentTime > BUFFER_HIGH_MARK_SECONDS) return true;

                // All other cases: Process additional frames
                await this.source.render(nextFrame, (frameNo, _, buffers) => {
                    // Bail on pausing.
                    if (this._paused) return false;

                    if (currentSecond - ctx.currentTime < BUFFER_LOW_MARK_SECONDS) {
                        ctx.suspend();
                    }

                    // Advance the frame counter.
                    nextFrame = frameNo+1;

                    // Build the AudioBuffer instances that we can construct.
                    // All of them are for exactly one full second.
                    const result = buildBuffer(this.source, lastBuffers, buffers, currentOffset, this.source.sample_rate);
                    currentOffset = result[1];
                    lastBuffers = buffers;

                    // Queue the samples.
                    for (let audio of result[0]) {
                        const node = new AudioBufferSourceNode(ctx, { buffer: audio });

                        node.connect(ctx.destination);
                        node.start(currentSecond++);
                    }

                    // Stop fetching additional chunks if we step over prefetch.
                    return currentSecond - ctx.currentTime < PREFETCH_SECONDS;
                });

                if (ctx.state === "suspended" && !this._paused)
                    await ctx.resume();

                return !this._paused;
            });
        } finally {
            ctx.close();
            this._onpause = null;
            this._paused = true;
        }
    }

    pause() {
        if (!!this._onpause)
            this._onpause();
        this._paused = true;
    }

    async open() {
        this.source.open();
        await this.source.loadMetadata();
    }
}

function buildBuffer(source: AudioSource, buffer1: ArrayBuffer[], buffer2: ArrayBuffer[], offset: number, length: number): [AudioBuffer[], number] {
    const b1 = buffer1[0].byteLength / 4;
    const b2 = buffer2[0].byteLength / 4;

    const lb = length - offset;

    let rest = b2 - lb;

    const result = [];


    if (offset >= 0) {
        const buffer = new AudioBuffer({
            length,
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
        const buffer = new AudioBuffer({
            length,
            sampleRate: source.sample_rate,
            numberOfChannels: source.channels
        });
        result.push(buffer);

        copyFromBuffers(buffer, buffer2, b2 - rest, 0);
        rest -= length;
    }

    return [ result, rest ];
}


function copyFromBuffers(buffer: AudioBuffer, channels: ArrayBuffer[], channelOffset: number, startOffset: number) {
    for (let channel = 0; channel<channels.length; channel++) {
        buffer.copyToChannel(new Float32Array(channels[channel], channelOffset*4), channel, startOffset);
    }
}
