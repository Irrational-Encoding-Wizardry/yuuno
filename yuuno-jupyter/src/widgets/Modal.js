import ModalComponent from '../components/Modal';
import Disposer from "../utils/Disposer";

export default class Modal extends Disposer{

    constructor(el) {
        super(null);
        this._state = false;
        this.el = el;
        this._parent = null;
    }

    setShown(state) {
        if (this._state === state) return;

        if (!this._parent)
            this._parent = this.el.parentNode;

        this._state = state;

        this.el.remove();
        if (this._state) {
            document.body.appendChild(this.el);
        } else {
            this._parent.appendChild(this.el);
        }
    }

    modalizeRender(store, hCb) {
        return (h) => store.state.modal.shown?h(ModalComponent, [hCb(h)]):hCb(h);
    }

    target() {
        this.setShown(false);
    }

}