import { Channel, Closable, RPCClient, RequestPacket, ResponsePacket, timeout } from "../../rpc";



interface AudioMeta {
    channel_count: number;
    sample_count: number;
    samples_per_second: number;
    frames: number;
}


export interface AudioRPC extends Closable {
    meta(): Promise<AudioMeta>;
    render(payload: { frame: number }): Promise<{ size: number, buffers: ArrayBuffer[] }>;
}



export class AudioSource implements Closable {
    private rpc: AudioRPC;
    private _open: boolean = false;

    private _channels: number = 0;

    private _frames: number = 0;
    
    private _loaded: number = 0;
    private _samples: number = 0;
    private _sample_rate: number = 0;

    ondata: () => void = () => {};

    constructor(channel: Channel<ResponsePacket, RequestPacket>) {
        this.rpc = new RPCClient(channel).makeProxy<AudioRPC>(timeout(10000));
    }

    open() {
        this.rpc.open();
        this._open = true;
    }

    close() {
        this._open = false;
        this.rpc.close();
    }

    get channels(): number {
        return this._channels;
    }

    get loaded(): number {
        return this._loaded;
    }

    get samples(): number {
        return this._samples;
    }

    get sample_rate(): number {
        return this._sample_rate;
    }

    get frames(): number {
        return this._frames;
    }

    get duration(): number {
        return this._samples / this._sample_rate;
    }

    async loadMetadata() {
        if (this._frames === 0) {
            const { frames, channel_count, samples_per_second, sample_count } = await this.rpc.meta();
            this._frames = frames;
            this._sample_rate = samples_per_second;
            this._samples = sample_count;
            this._channels = channel_count
        }
        this.ondata();
    }

    async render(start: number, received: (frameno: number, size: number, buffers: ArrayBuffer[]) => boolean) {
        if (this._frames === 0)
            await this.loadMetadata();

        for (let frame = start; frame<this._frames; frame++) {
            if (!this._open) break;

            const { size, buffers } = await this.rpc.render({ frame });
            this._loaded += size;

            if (!received(frame, size, buffers))
                break;
        }
    }

}
