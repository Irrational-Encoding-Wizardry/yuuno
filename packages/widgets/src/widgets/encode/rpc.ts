import { Channel, Closable, RPCClient, RequestPacket, ResponsePacket, timeout } from "../../rpc";


export interface EncodeRPC extends Closable {

    kill(): Promise<any>;

    interrupt(): Promise<any>;

    refresh(payload: { source: string }): Promise<{ data: string }>;

}

export function getRPCForModel(channel: Channel<ResponsePacket, RequestPacket>): EncodeRPC {
    return new RPCClient(channel).makeProxy(timeout(10000));
}
