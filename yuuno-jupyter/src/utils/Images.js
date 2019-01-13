import Worker from "worker-loader?inline=true&name=worker.js&publicPath=/nbextensions/yuuno-ipython/!./images/impl.worker";
import Disposer from './Disposer';
import { RequestReply } from './RequestReply';
import { MessageConnection } from './Connection';
import MessagablePool from "./MessageablePool";


const pool = new MessagablePool({
    create: () => new Worker(),
    destroy: (worker) => worker.terminate(),

    maxlife: 30 * 1000,
    create_life: 5 * 1000,
    maxsize: 5,
});
const reqrepl = new RequestReply(new MessageConnection(pool));


export default class ImageOperations extends Disposer {

    constructor() {
        super(null);
    }

    async _do_request(type, data) {
        return (await reqrepl.send({
            type: type,
            payload: data
        })).payload;
    }

    async resizeImage(pngBuffer, w, h) {
        return (await this._do_request("resize", {w, h, buffer: pngBuffer.buffer})).resized;
    }

    target() {
    }
}