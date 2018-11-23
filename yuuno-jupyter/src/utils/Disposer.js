export default class Disposer {

    constructor(target) {
        this._disposed = false;
        this._target = target;
        this._disposers = [];
    }

    addDisposer(callback) {
        this._disposers.push(callback);
    }

    target() {
        const $this = this;

        return () => {
            $this._target();
            $this._target = () => undefined;
        }
    }

    isDisposed() {
        return this._disposed;
    }

    dispose() {
        this._disposed = true;
        this.target();
        for (var disposer of this._disposers)
            disposer();
    }

}