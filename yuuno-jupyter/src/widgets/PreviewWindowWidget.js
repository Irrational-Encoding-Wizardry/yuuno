import { DOMWidgetView } from '@jupyter-widgets/base';
import Vue from 'vue';
import {Store, mapState} from 'vuex';
const download_data = require('downloadjs');

import RateLimit from '../utils/RateLimit';
import PromiseDelegate from '../utils/PromiseDelegate';
import VuexBackboneValueBridge from '../utils/VuexBackboneValueBridge';

import {emptyElement, createMountedElement} from '../utils/domUtils';
import Modal from '../components/Modal';
import FrameCache from '../utils/frameCache';

import PreviewWindow from '../components/PreviewWindow';
const nextTick = require('next-tick');


let _widget_counter_id = 0;
const _frame_cache = new FrameCache(20);

export default class PreviewWindowWidget extends DOMWidgetView {
    render() {
        const $this = this;
        this._id_widget = _widget_counter_id++;
        this._rate_limit = new RateLimit(150);

        this._state = new Store({
            state: {
                model: {},
                length: 0,

                image: {
                    size: {
                        width: 0,
                        height: 0
                    },
                    raw: null
                },

                updating: 0,
                in_modal: false
            },

            mutations: {
                import(state, {name, value}) {
                    Vue.set(state.model, name, value);
                },

                switchModal(state) {
                    state.in_modal = !state.in_modal;
                },

                setLength(state, length) {
                    state.length = length;
                },

                setImage(state, {raw, size}) {
                    state.image.raw = raw;
                    state.image.size.width = size.width;
                    state.image.size.height = size.height;
                },

                setUpdating(state, update_state) {
                    state.updating += update_state?1:-1;
                }
            },

            actions: {
                downloadImage({state}) {
                    download_data(new Blob([state.image.raw]), `Preview${state.model.frame}.png`, "image/png");
                },

                async update({commit}, cb) {
                    commit('setUpdating', true);
                    try {
                        await cb();
                    } finally {
                        commit('setUpdating', false);
                    }
                },

                async computeLength({commit, dispatch}) {
                    await dispatch('update', async () => {
                        const result = await $this._send_request('length', null);
                        commit('setLength', result.payload);
                    })
                },

                async renderFrame({commit, dispatch, state}) {
                    $this._rate_limit.fire(async () => {
                        await dispatch('update', async () => {
                            const result = await $this._request_frame();
                            commit('setImage', {raw: result.buffers[0], size: {width: result.payload.size[0], height: result.payload.size[1]}});
                        });
                    });
                },

                toggleModal({commit, state}) {
                    commit('switchModal');
                    $this._vue.$el.remove();
                    if (state.in_modal) {
                        document.body.appendChild($this._vue.$el);
                    } else {
                        $this.el.appendChild($this._vue.$el);
                    }
                }
            }
        });
        this._vue = new Vue({
            store: this._state,
            render: function (h) {return !this.in_modal?h(PreviewWindow):h(Modal, [h(PreviewWindow)])},
            computed: {
                ...mapState({
                    in_modal: (state) => state.in_modal
                })
            }
        });
    
        emptyElement($this.el);
        const subEl = createMountedElement($this.el, 'div');
        nextTick(() => $this._renderActuallyAttached(subEl));

        this.model.on('msg:custom', this._handle_custom_msg, this);

        this._request_ids = 0;
        this._internal_request_map = {}
        this._synchronizer = VuexBackboneValueBridge(this.model, this._state, ['clip', 'frame', 'zoom'], () => this.touch());

        this._state.dispatch('computeLength');
        this._state.dispatch('renderFrame');
    }

    _handle_custom_msg(content, buffers) {
        if (content.type === 'response') {
            const {id, payload} = content;
            if (!this._internal_request_map[id]) return;
            this._internal_request_map[id].resolve({payload, buffers});
        } else if (content.type === 'failure') {
            const {id, payload} = content;
            if (!this._internal_request_map[id]) return;
            this._internal_request_map[id].reject({payload, buffers});
        }
    }

    async _request_frame() {
        const frame = this.model.get('frame');
        const clip = this.model.get('clip');
        return (await _frame_cache.get(`${clip}--${frame}`, async () => await this._send_request('frame', null)));
    }

    _send_request(type, data, buffers=[]) {
        const id = `${this._id_widget}--${++this._request_ids}`;
        const delegate = new PromiseDelegate();
        this._internal_request_map[id] = delegate;
        this.send({
            'type': type,
            'id': id,
            'payload': data
        }, buffers);
        return delegate.promise;
    }

    _renderActuallyAttached(target) {
        this._vue.$mount(target);
    }

    remove() {
        this._synchronizer.dispose();
        this._vue.$destroy();
        this.model.off('msg:custom', this._handle_custom_msg, this);

        super.remove();
    }
};
