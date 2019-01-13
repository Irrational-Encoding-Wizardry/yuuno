import Disposer from '../../utils/Disposer';
import FrameCache from '../../utils/FrameCache';
import { WidgetRequestReply } from '../../utils/RequestReply';
import VuexBackboneBridge from '../../utils/VuexBackboneValueBridge';


const cache = new FrameCache({max: 10});


export default class PreviewModel extends Disposer {
    constructor(widget) {
        super();
        this.widget = widget;
        this.reqrepl = new WidgetRequestReply(widget);
    }

    bind(store, {namespace}) {
        const disp = VuexBackboneBridge(this.widget.model, {vuex: store, moduleName: namespace}, ['clip', 'diff', 'frame', 'zoom'], () => this.widget.touch());
        this.addDisposer(() => disp.dispose());
    }

    async _rawRequest(content, buffers) {
        const data = await this.reqrepl.send({...content, $buffers: buffers});
        buffers = data.$buffers;
        delete data['$buffers'];
        return [data.payload, buffers]
    }

    async requestFrame(type) {
        // Make sure we don't have a race condition and always send the requested frame.
        return await cache.get(`frame-${this.widget.model.get(type)}-${this.widget.model.get('frame')}`, async()=>{
            return await this._rawRequest({type: 'frame', payload: {image: type, frame: this.widget.model.get('frame')}});
        });
    }

    async requestMeta(type) {
        return await cache.get(`meta-${this.widget.model.get(type)}-${this.widget.model.get('frame')}`, async()=>{
            return await this._rawRequest({type: 'metadata', payload: {image: type, frame: this.widget.model.get('frame')}});
        });
    }

    async requestLength(type) {
        const [payload, buffers] = await this._rawRequest({type: 'length', payload: {image: type}})
        payload.clip_id = this.widget.model.get(type);
        return [payload, buffers];
    }

    _target() {
        this.reqrepl.dispose();
    }
    
}