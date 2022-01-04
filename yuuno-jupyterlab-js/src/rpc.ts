
export type Subscriber<T> = (value: T) => void;
export type Unsubscriber = () => void;



type ResponseAwaiter<T> = (value: T) => void;


export type FinishedNormally = () => void;
export type Canceler = () => void;
export type CancelRendezVous = (cancel: Canceler) => FinishedNormally;


let _instance_counter = 0;


export interface Packet {
    id: string
    payload: any;
    buffers?: ArrayBuffer[];
}

export interface RequestPacket extends Packet {
    type: string;
}

export interface ResponsePacket extends Packet {
    type: "failure"|"response";
}

export interface Channel<Receive extends Packet, Send extends Packet> {
    /**
     * Sends a message through this channel.
     */
    send(message: Send): Promise<void>;

    /**
     * Subscribe to messages.
     */
    subscribe(subscriber: Subscriber<Receive>): Unsubscriber;
}



export interface Closable {
    open(): void
    close(): void
}


export class RPCServer<T> {
    private functions: T;
    private channel: Channel<RequestPacket, ResponsePacket>;

    private subscription: Unsubscriber|null;

    constructor(functions: T, channel: Channel<RequestPacket, ResponsePacket>) {
        this.functions = functions;
        this.channel = channel;
        this.subscription = null;
    }

    _closeSubscription() {
        if (this.subscription !== null) {
            this.subscription();
            this.subscription = null;
        }
    }

    open() {
        this._closeSubscription();
        this.subscription = this.channel.subscribe((p: RequestPacket) => this._receive(p).catch(console.log));
    }

    close() {
        this._closeSubscription();
    }

    async _send(packet: ResponsePacket) {
        if (this.subscription === null) return;
        this.channel.send(packet);
    }

    async _receive(packet: RequestPacket) {
        if (!packet.id) {
            await this._send({
                id: "",
                type: "failure",
                payload: "Unknown ID"
            });
            return;
        }

        if (!packet.type) {
            await this._send({
                id: packet!.id,
                type: "failure",
                payload: "No method called."
            });
            return;
        }

        if (!(packet.type in this.functions)) {
            await this._send({
                id: packet.id,
                type: "failure",
                payload: "Unknown method."
            });
            return;
        }

        let input_buffers: ArrayBuffer[] = [];
        if (!!packet.buffers) {
            input_buffers = packet.buffers;
            delete packet.buffers;
        }

        let result: any = undefined;
        try {
            let raw_result: any = this.functions[packet.type as keyof T]
            let p_result = raw_result(packet.payload, input_buffers);
            if ("then" in p_result)
                result = await p_result;
            else
                result = raw_result;
        } catch (e) {
            await this._send({
                id: packet.id,
                type: "failure",
                payload: e.toString()
            })
            return;
        }

        let buffers = [];
        if ("buffers" in result) {
            buffers = result.buffers;
            delete result["buffers"];
        }

        await this._send({
            id: packet.id,
            type: "response",
            payload: result,
            buffers: buffers
        })
    }

}



export class RPCClient {
    private _requests: Map<string, ResponseAwaiter<ResponsePacket>>;
    private _instance_number: number;
    private _current_packet_counter: number;

    private channel: Channel<ResponsePacket, RequestPacket>;
    private subscription: Unsubscriber|null;

    constructor(channel: Channel<ResponsePacket, RequestPacket>) {
        this._requests = new Map();
        this._instance_number = _instance_counter++;
        this._current_packet_counter = 0;

        this.channel = channel;
        this.subscription = null;
    }

    _closeSubscription() {
        if (this.subscription !== null) {
            this.subscription();
            this.subscription = null;
        }
    }

    open() {
        this._closeSubscription();
        this.subscription = this.channel.subscribe((pkt) => this._receive(pkt));
    }

    _receive(packet: ResponsePacket) {
        // Drop packets not for us.
        if (!this._requests.has(packet.id)) return;
        const awaiter = this._requests.get(packet.id)!;
        this._requests.delete(packet.id);
        awaiter(packet);
    }

    makeProxy<T>(cancel: CancelRendezVous|undefined): T&Closable {
        const cache: any = {
            open: () => this.open(),
            close: () => this.close()
        };
        return new Proxy(cache, {
            get: (_, name) => {
                return name in cache
                    ? cache[name]
                    : (cache[name] = (payload: any = {}, buffers: ArrayBuffer[]|undefined = undefined) => {
                        return this.request(name.toString(), payload, buffers, cancel);
                      })
                    ;
            }
        }) as T&Closable;
    }

    request<T>(
            name: string,
            payload: any,
            buffers: ArrayBuffer[]|undefined = undefined,
            cancel: CancelRendezVous|undefined
    ): Promise<T> {
        const id = `${this._instance_number}--${this._current_packet_counter++}`;
        return new Promise((rs, rj) => {
            let finished = () => {}
            const awaiter = (packet: ResponsePacket) => {
                finished();
                if (!!packet.buffers) {
                    packet.payload.buffers = packet.buffers;
                }

                if (packet.type == "failure") {
                    rj(packet.payload);
                } else {
                    rs(packet.payload as T);
                }
            };

            if (cancel !== undefined) {
                finished = cancel(() => {
                    this._requests.delete(id);
                    rj();
                });
            }

            this._requests.set(id, awaiter);
            this.channel.send({
                id,
                type: name,
                payload,
                buffers
            })
        });
    }

    close() {
        this._closeSubscription();
    }
}


export function timeout(time: number): CancelRendezVous {
    return (cancel) => {
        const id = setTimeout(() => cancel(), time);
        return () => clearTimeout(id);
    }
}

export function race(other: Promise<any>): CancelRendezVous {
    return (cancel) => {
        other.then(
            () => cancel(),
            () => cancel()
        );

        return () => {}
    }
}
