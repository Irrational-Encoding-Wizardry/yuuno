import type { DOMWidgetModel } from "@jupyter-widgets/base";
import { Closable, RPCClient, RequestPacket, ResponsePacket, timeout } from "../../rpc";
import { WidgetChannel } from "../../model-rpc";


export interface EncodeRPC extends Closable {

    kill(): Promise<any>;

    interrupt(): Promise<any>;

    refresh(payload: { source: string }): Promise<{ data: string }>;

}

export function getRPCForModel(model: DOMWidgetModel): EncodeRPC {
    const channel = new WidgetChannel<ResponsePacket, RequestPacket>(model);
    return new RPCClient(channel).makeProxy(timeout(10000));
}
