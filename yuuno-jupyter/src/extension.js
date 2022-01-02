import Vue from 'vue';
import Vuex from 'vuex';
Vue.config.devtools = true;
Vue.use(Vuex);

export {default as PreviewWindowWidget} from './widgets/PreviewWindow';
export {default as EncodeWindowWidget} from './widgets/EncodeWindow';

alert("Yuuno for Jupyter Notebook will only be supported in Yuuno 1.4. It also does not support Audio.");
