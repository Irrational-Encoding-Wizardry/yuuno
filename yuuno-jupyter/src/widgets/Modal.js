import Disposer from '../utils/Disposer';
import Vue from 'vue';
const {Modal: VueModal} = require('../components/Modal');
import {createMountedElement} from '../utils/domUtils';
const nextTick = require('next-tick');


export default class Modal extends Disposer {

    constructor(el) {
        super(null);
        this._el = el;
        this._original_parent = this._el.parent;

        this._shown = false;
        this._modal_el = null;
        this._modal_parent = document.body;
        this._vue = null;
    }

    setShown(state) {
        if (this._shown === state) return;
        this._shown = state;

        if (this._shown) {
            this._modal_el = createMountedElement(this._modal_parent, 'div');
            this._vue = new Vue({
                render: (h) => h(VueModal, [h("div", {ref: "target"})]),

                beforeUpdate() {
                    if (this.$refs["target"].firstChild === $this._el) return;
                    while (this.$refs["target"].firstChild)
                        this.$refs["target"].firstChild.remove();
                    this.$refs.appendChild($this._el);
                }
            });
            nextTick(() => this._vue.$mount(this._modal_el), this);
        } else {
            this._el.remove();

            this._vue.$destroy();
            this._vue = null;

            this._original_parent.appendChild(this._el);
            if (!!this._modal_el) {
                this._modal_el.remove();
                this._modal_el = null;
            }
        }
    }

    target() {
        this.setShown(false);
    }

}