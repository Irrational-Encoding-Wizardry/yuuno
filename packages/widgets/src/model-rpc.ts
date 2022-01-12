import { Channel, Packet, Subscriber, Unsubscriber } from "./rpc";
import { WidgetModel } from '@jupyter-widgets/base';


export class WidgetChannel<Receive extends Packet, Send extends Packet> implements Channel<Receive, Send> {
    private model: WidgetModel;

    constructor(model: WidgetModel) {
        this.model = model;
    }
    
    /**
     * Sends a message through this channel.
     */
    async send(message: Send): Promise<void> {
        const buffers = ("buffers" in message ? message.buffers : []) || [];
        if ("buffers" in message) delete message["buffers"];

        this.model.send(message, buffers);
    }

    /**
     * Subscribe to messages.
     */
    subscribe(subscriber: Subscriber<Receive>): Unsubscriber {
        const cb = (content: Receive, buffers: ArrayBuffer[]|ArrayBufferView[]) => {
            if (buffers.length > 0) {
                content.buffers = (buffers as (ArrayBuffer|ArrayBufferView)[]).map((b: ArrayBuffer|ArrayBufferView) => {
                    if (b instanceof ArrayBuffer) {
                        return b;
                    } else {
                        var dst = new ArrayBuffer(b.byteLength);
                        new Uint8Array(dst).set(new Uint8Array(b.buffer));
                        return dst;
                    }
                });
            }
            subscriber(content);
        };

        this.model.on("msg:custom", cb);
        return () => {
            this.model.off("msg:custom", cb);
        };
    };
}
