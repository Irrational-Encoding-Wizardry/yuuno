import Vue from 'vue';
import Vuex from 'vuex';
Vue.config.devtools = true;
Vue.use(Vuex);

export {default as PreviewWindowWidget} from './widgets/PreviewWindowWidget';
export {default as EncodeWindowWidget} from './widgets/EncodeWindowWidget';
