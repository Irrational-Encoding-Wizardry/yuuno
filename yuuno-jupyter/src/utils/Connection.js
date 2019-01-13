export class Connection {

    constructor() {
    }

    send(data, binaries) {

    }

    receive(data, binaries) {
        console.log(data, binaries, this);
    }

}


export class WidgetConnection extends Connection {
    constructor(widget) {
        super();
        this.widget = widget;
        this.widget.model.on('msg:custom', (...args) => this.receive(...args), this);
    }


    send(data, binaries) {
        this.widget.send(data, binaries);
    }
}


export class MessageConnection extends Connection {
    constructor(message) {
        super();
        this.message = message;
        this.message.onmessage = (event) => this.receive(event.data.data, event.data.binaries);
    }

    send(data, binaries) {
        this.message.postMessage({data, binaries}, binaries);
    }
}


export class ChildConnection extends Connection {
    constructor(parent) {
        super();
        this.parent = parent;
        this.parent.receive = (...args) => this.receive(...args);
        console.log(this.parent, this, this.parent.receive);
    }

    send(data, binaries) {
        this.parent.send(data, binaries);
    }
}


class MultiplexerConnection extends Connection {
    constructor(parent, name) {
        super();
        this.parent = parent;
        this.name = name;
    }

    send(data, binaries) {
        this.parent.send({target: this.name, payload: data}, binaries);
    }
}


export class MultiplexedConnection extends ChildConnection {
    constructor(parent) {
        super(parent);
        this.targets = {};
    }

    register(name) {
        const conn = new MultiplexerConnection(this, name);
        this.targets[name] = conn;
        return conn;
    }

    unregister(name) {
        delete this.targets[name];
    }

    receive(data, binaries) {
        const {target, payload} = data;
        if (!this.targets[target]) return;
        this.targets[target].receive(payload, binaries);
    }
}