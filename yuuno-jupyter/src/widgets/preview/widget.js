import VueWidget from '../VueWidget';
import Modal from '../Modal';

import PreviewModel from './model';
import makeStore from './store';
import Vue from 'vue';

import PreviewWindowComponent from '../../components/preview/PreviewWindow';


export default class PreviewWidget extends VueWidget {

    render() {
        this._pw_model = new PreviewModel(this);
        const el = this.el;

        this._store = this._store || makeStore(this._pw_model);
        this._modal = new Modal(this.el);
        this._store.watch((state) => state.modal.shown, (v) => this._modal.setShown(v));
        super.render();

        this._store.dispatch('fetchLengths');
    }

    create_vue() {
        return new Vue({
            store: this._store,
            render: this._modal.modalizeRender(this._store, (h) => h(PreviewWindowComponent))
        });
    }

    remove() {
        this._pw_model.dispose();
        this._modal.dispose();
        super.remove();
    }

}