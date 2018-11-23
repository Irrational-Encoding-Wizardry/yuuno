import LRU from 'lru-cache';
import PromiseDelegate from './PromiseDelegate';


export default class LRUCache {

    constructor(options) {
        this._lru = new LRU(options);
        this._active = {};
    }

    async get(target, cb) {
        if (!!this._active[target])
            return (await this._active[target]);

        const delegate = new PromiseDelegate();
        this._active[target] = delegate.promise;

        let result;
        if ((result = this._lru.get(target)) !== undefined)
            return delegate.resolve(result);

        try {
            result = await cb();
            this._lru.set(target, result);
            delegate.resolve(result);
        } catch (e) {
            delegate.reject(e);
        }

        return delegate.promise;
    }

}