class PoolContainer {
    constructor(instance, destroy) {
        this.instance = instance;
        this.destroy = destroy;
        this.last_message = 0;
    }

    dispose() {
        this.destroy(this.instance);
    }

    expired(maxlife) {
        return (Number(new Date()) - this.last_message) > maxlife;
    }

    setCallback(callback) {
        this.instance.onmessage = callback;
    }

    postMessage(...args) {
        this.last_message = Number(new Date());
        this.instance.postMessage(...args);
    }
}


export default class MessagablePool {

    constructor(options) {
        this.minsize = options.minsize || 1;
        this.maxsize = options.maxsize || 10;
        this.maxlife = options.maxlife || (60 * 1000);
        this.create_life = options.create_life || (1 * 1000);
        this.create  = options.create;
        this.destroy = options.destroy;

        this._interval = setInterval(() => this._refresh(), 1000);
        this.onmessage = null;
        this._last_message = 0;
        this._pool = [];
    }

    _refresh() {
        for (let worker of Array.from(this._pool)) {
            if (this._pool.length <= this.minsize) return;
            if (!worker.expired(this.maxlife)) continue;
            worker.dispose();
            this._pool.splice(this._pool.indexOf(worker), 1);
        }
    }

    _next_worker() {
        let worker;
        if (this._pool.length < this.maxsize) {
            if (this._pool.length > 0 && (Number(new Date()) - this._last_message) > this.create_life) {
                worker = this._pool.shift();
            } else {
                worker = new PoolContainer(this.create(), this.destroy);
                worker.setCallback((...args) => (this.onmessage||(()=>undefined))(...args));
            }
        } else {
            worker = this._pool.shift();
        }
        return worker;
    }

    postMessage(...args) {
        const worker = this._next_worker();
        worker.postMessage(...args);
        this._last_message = Number(new Date());
        this._pool.push(worker);
    }

}