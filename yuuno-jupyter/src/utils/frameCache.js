import LRU from 'lru-cache';
import PromiseDelegate from './PromiseDelegate';


export default class LRUCache {

    constructor(options) {
        this._lru = new LRU(options);
        this._active = {};
    }

    async get(target, cb) {
        let result;
        if ((result = this._lru.get(target)) !== undefined) {
            return result;
        }

        if (!!this._active[target])
            return (await this._active[target]);

        const delegate = new PromiseDelegate();
        this._active[target] = delegate.promise;
        delegate.promise.then(
            () => delete this._active[target],
            () => delete this._active[target]
        );

        try {
            result = await cb();
            this._lru.set(target, result);
            delegate.resolve(result);
        } catch (e) {
            delegate.reject(e);
        }

        return await delegate.promise;
    }

}