import Disposer from './Disposer';
import PromiseDelegate from './PromiseDelegate';


let _inst_ctr = 0;


export class RequestReply extends Disposer {

    constructor() {
        super(null);
        this._requests = {};
        this._instance = _inst_ctr++;
        this._current_id = 0;
    }

    target() {
        for (let k of Objects.keys(this._requests)) {
            this._requests[k].reject(new Error("Manager was disposed"));
        }
        this._requests = {}
    }

    _send(data) {

    }

    receive(data) {
        const id = data.id;
        if (!this._requests[id]) return;
        const delegate = this._requests[id];

        if (data.type === "failure")
            delegate.reject(new Error(data.payload));
        else
            delegate.resolve(data);

        delete this._requests[id];
    }

    send(data) {
        const id = `${this._instance}--${this._current_id++}`;
        const delegate = this._requests[id] = new PromiseDelegate();
        this._send({
            id,
            ...data
        });
        return delegate.promise;
    }
}

export class WidgetRequestReply extends RequestReply {
    constructor(widget) {
        super();
        this.widget = widget;
        this.widget.model.on('msg:custom', this.receive, this);
    }

    _send(data) {
        const buffers = data.$buffers || [];
        delete data['$buffers'];
        this.widget.send(data, buffers);
    }

    target() {
        this.widget.model.off('msg:custom', this._receive, this);
        super.target();
    }

    receive(content, buffers) {
        content.$buffers = buffers;
        super.receive(content);
    }
}

export class MessageRequestReply extends RequestReply {
    constructor(messagable) {
        super();
        this.messagable = messagable;
        this._previous = this.messagable.onmessage;
        this.messagable.onmessage = (event) => this.receive(event.data);
    }

    _send(data) {
        const transfers = data.$transfers || [];
        delete data['$transfers'];
        this.messagable.postMessage(data, transfers);
    }

    target() {
        this.messagable.onmessage = this._previous;
        super.target();
    }
}