import {mapState} from 'vuex';

export function modelReadWrite(states) {
    const computed = {}
    const mappedStates = mapState(states);
    Object.keys(states).forEach((name) => {
        computed[name] = {
            get: mappedStates[name],
            set: function(value){this.$store.commit('model/sync', {key: name, value})},
            vuex: true
        }
    })
    return computed;
}