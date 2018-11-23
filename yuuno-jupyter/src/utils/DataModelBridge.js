import Disposer from './Disposer';


export class Binding extends Disposer {

    constructor(dmb, id) {
        super(null);
        this._dmb = dmb;
        this._id = id;
    }

    setValue(value) {
        if (this.isDisposed()) throw new Error("Binding is disposed.");
        return this._dmb.set(value, this._id);
    }

    target() {
        delete this._dmb[this._id];
        this._dmb = null;
        this._id = null;
    }

}


export default class DataModelBridge {

    constructor() {
        this.currentId = 0
        this.endpoints = {};
        this._value = undefined;
    }

    add(callback) {
        const id = this.currentId++;
        const binding = new Binding(this, id);
        this.endpoints[id] = { callback, binding };
        return binding;
    }

    set(value, id=null) {
        if (this._value === value) return;

        this._value = value;
        for (var vId of Object.keys(this.endpoints)) {
            if (vId == id) continue;
            this.endpoints[vId].callback(value);
        }
    }

    dispose() {
        for (var vId of Object.keys(this.endpoints)) {
            this.endpoints[vId].binding.dispose();
        }
        this.endpoints = {};
    }
}