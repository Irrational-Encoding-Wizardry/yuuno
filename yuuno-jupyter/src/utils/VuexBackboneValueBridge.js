import DataModelBridge from './DataModelBridge';
import Disposer from './Disposer';


function attachBackbone(bridge, backbone_model, name) {
    const binding = bridge.add((value) => backbone_model.set({[name]: value}));
    const changer = () => binding.setValue(backbone_model.get(name));
    backbone_model.on(`change:${name}`, changer);
    binding.addDisposer(() => backbone_model.off(`change:${name}`, changer));
    return binding;
}

function syncToVuex(binding, payload) {
    const {vuex, moduleName} = binding;

    let mutationName;
    if (!!moduleName) mutationName = `${moduleName}/sync`;
    else              mutationName = 'sync';

    vuex.commit(mutationName, payload);
}

function attachVueX(bridge, storeBinding, name) {
    const {vuex} = storeBinding;
    const binding = bridge.add((value) => syncToVuex(storeBinding, {key: name, value}));
    const unwatch = vuex.watch((state) => state.model[name], (value) => binding.setValue(value));
    binding.addDisposer(() => unwatch());
    return binding;
}

export default function VuexBackboneBridge(backbone_model, vuex, names, cb=null) {
    const bridges = [];

    names.forEach((name) => {
        const bridge = new DataModelBridge();
        syncToVuex(vuex, {key: name, value: backbone_model.get(name)});
        attachBackbone(bridge, backbone_model, name);
        attachVueX(bridge, vuex, name);
        if (!!cb) bridge.add((value) => cb(name, value));
        bridges.push(bridge);
    });

    return new Disposer(() => {
        for (var bridge of bridges)
            bridge.dispose();
    });
}