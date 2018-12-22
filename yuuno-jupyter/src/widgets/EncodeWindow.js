import { DOMWidgetView } from '@jupyter-widgets/base';
import EncodeWindowComponent from '../components/encode/EncodeWindow';
import Vue from 'vue';

const nextTick = require('next-tick');
let _widget_id = 0;


export default class EncodeWindow extends DOMWidgetView {
    render() {
        const $this = this;
        this._own_widget_id = _widget_id++;
        this._vue = new Vue({
            name: 'Encode',
            render: function(h) {
                return h(EncodeWindowComponent, {
                    ref: 'encode',
                    props: {
                        current: this.current,
                        length: this.length,
                        terminated: this.terminated,

                        start_time: $this.model.get('start_time'),
                        end_time: $this.model.get('end_time'),

                        _win32: $this.model.get('_win32')
                    },
                    on: {
                        'interrupt-process': () => $this.send({'type': 'interrupt'}),
                        'kill-process': () => $this.send({'type': 'kill'})
                    }
                });
            },
      
            data: {
                terminated: this.model.get('terminated'),
                current: this.model.get('current'),
                length: this.model.get('length'),

                mountingComplete: false,
                writePrep: []
            },
            mounted() {
                for (var data of this.writePrep) {
                    this.$refs['encode'].write(data);
                }
                this.writePrep = [];
                this.mountingComplete = true;
            },

            methods: {
                write(data) {
                    if (!this.mountingComplete) {
                        this.writePrep.push(data);
                        return;
                    }
                    this.$refs['encode'].write(data);
                }
            }
        });
        nextTick(() => this._vue.$mount(this.el));

        this.model.on('msg:custom', this._handle_custom_msg, this);
        this.model.on('change:length', this._sync_progress, this);
        this.model.on('change:current', this._sync_progress, this);
        this.model.on('change:terminated', this._sync_termination, this);
        this.model.on('change:end_time', this._sync_end_time, this)

        this._accept_broadcast = false;
        this.send({'type': 'refresh', 'source': this._own_widget_id});
    }

    _handle_custom_msg(content, buffers) {
        if(content.target === "broadcast" && !this._accept_broadcast)
            return;
        if (!(content.target === "broadcast" || content.target === this._own_widget_id))
            return;

        if (content.type === "write")
            this._vue.write(content.data);

        if (content.type === "refresh_finish")
            this._accept_broadcast = true;
    }

    _sync_progress() {
        this._vue.current = this.model.get("current");
        this._vue.length = this.model.get("length");
    }

    _sync_termination() {
        this._vue.terminated = this.model.get('terminated')
    }

    _sync_end_time() {
        this._vue.end_time = this.model.get('end_time')
    }

    remove() {
        this.model.off('change:length', this._sync_progress, this);
        this.model.off('change:end_time', this._sync_termination, this);
        this.model.off('change:terminated', this._sync_termination, this);
        this.model.off('change:progress', this._sync_progress, this);
        this._vue.$destroy();
        super.remove();
    }
}