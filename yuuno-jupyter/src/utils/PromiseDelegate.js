export default class PromiseDelegate {

    constructor() {
        let _cbs = [];
        this._operation = (cb) => _cbs.push(cb);
        this._promise = new Promise((rs, rj) => {
            this._operation = (cb) => cb(rs, rj);
            _cbs.forEach((cb) => cb(rs, rj));
            _cbs.length = 0;
        });
    }

    get promise() {
        return this._promise;
    }

    resolve(...args) {
        this._operation((rs, rj) => rs(...args));
    }

    reject(...args) {
        this._operation((rs, rj) => rj(...args));
    }

}