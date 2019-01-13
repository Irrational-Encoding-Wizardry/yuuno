import Disposer from './Disposer';
import PromiseDelegate from './PromiseDelegate';


let _inst_ctr = 0;


export class RequestReply extends Disposer {

    constructor(connection) {
        super(null);
        this._requests = {};
        this._instance = _inst_ctr++;
        this._current_id = 0;

        this.connection = connection;
        this.connection.receive = (data, binaries) => this.receive(data, binaries);
    }

    target() {
        for (let k of Objects.keys(this._requests)) {
            this._requests[k].reject(new Error("Manager was disposed"));
        }
        this._requests = {}
    }

    receive(data, buffers) {
        const id = data.id;
        data.$buffers = buffers;
        if (!this._requests[id]) return;
        const delegate = this._requests[id];

        if (data.type === "failure")
            delegate.reject(new Error(data.payload));
        else
            delegate.resolve(data);

        delete this._requests[id];
    }

    send(data, binaries) {
        const id = `${this._instance}--${this._current_id++}`;
        const delegate = this._requests[id] = new PromiseDelegate();
        this.connection.send({
            id,
            ...data
        }, binaries);
        return delegate.promise;
    }
}