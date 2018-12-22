import { DOMWidgetView } from '@jupyter-widgets/base';

const nextTick = require('next-tick');
import { createMountedElement } from '../utils/DOMUtils';


export default class VueWidget extends DOMWidgetView {
    render() {
        const el = createMountedElement(this.el, 'div');
        
        if (!this._vue) {
            const _vue = this.create_vue();
            this._vue = _vue;
            nextTick(() => _vue.$mount(el));
        }
        super.render();
    }

    create_vue() {}

    remove() {
        if (!!this._vue)
            this._vue.$destroy();
        super.render();
    }
}