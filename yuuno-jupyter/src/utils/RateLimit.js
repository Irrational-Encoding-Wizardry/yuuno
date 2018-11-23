export default class RateLimit {

    constructor(timer) {
        this._timer = timer;
        this._handle = null;
        this._updated = false;
        this._callback = null;
    }

    fire(exec_cb, discard_cb=(() => undefined)) {
        if (this._handle === null)
            this._handle = setInterval(() => this._tick(), this._timer);

        if (this._callback !== null)
            this._callback.discard_cb();

        this._callback = {exec_cb, discard_cb};

        this._updated = true;
    }

    _tick() {
        if (!this._updated) {
            clearInterval(this._handle);
            this._handle = null;
            this._callback.exec_cb();
            this._callback = null;
        } else {
            this._updated = false;
        }
    }

}