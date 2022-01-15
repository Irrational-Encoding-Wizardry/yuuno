import type Backbone from "backbone";
import { Channel, Closable, RPCClient, RequestPacket, ResponsePacket, timeout } from "../../rpc";


export interface PreviewRPC extends Closable {
    /**
     * Returns the length of the clip
     */
    length(): Promise<{ length: number }>;

    /**
     * Let the preview window render a frame.
     *
     * @param frame  The frame number.
     */
    frame(payload: {frame: number, image?: 'clip'|'diff'}): Promise<{ size: [number, number], buffers?: ArrayBuffer[] }>;
}


class CachedPreviewRPC implements PreviewRPC {
    private _cache: Map<string, Promise<{ size: [number, number], buffers?: ArrayBuffer[] }>> = new Map();
    private _lru: string[] = [];

    private parent: PreviewRPC;
    private model: Backbone.Model;

    constructor(parent: PreviewRPC, model: Backbone.Model) {
        this.parent = parent;
        this.model = model;
    }

    clear() {
        this._cache.clear();
    }

    open() {
        this.parent.open();
    }

    close() {
        this.parent.close();
    }

    length() {
        return this.parent.length();
    }

    frame(
            { frame, image }: { frame: number, image?: 'clip'|'diff' }
    ): Promise<{ size: [number, number], buffers?: ArrayBuffer[] }> {
        if (!image) image = "clip";
        const realId = this.model.get("clips")[this.model.get(image)];
        const _lru_id = `${realId}--${image}--${frame}`;
        if (!this._cache.has(_lru_id)) {
            this._evict();
            this._cache.set(_lru_id, this.parent.frame({ frame, image }));
        }
        this._hit(_lru_id);
        return this._cache.get(_lru_id)!;
    }

    private _hit(id: string) {
        if (this._lru.indexOf(id) == 0) 
            return;

        this._lru = [id, ...this._lru.filter(f => f != id)]
    }

    private _evict() {
        if (this._lru.length <= 10) return;
        const evicted = this._lru.pop()!;
        this._cache.delete(evicted);
    }
}


export function getRPCForModel(model: Backbone.Model, channel: Channel<ResponsePacket, RequestPacket>): PreviewRPC {
    return new CachedPreviewRPC(new RPCClient(channel).makeProxy(timeout(10000)), model);
}
