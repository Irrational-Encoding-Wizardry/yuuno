import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);


const createImageModule = function() {
    return {
        namespaced: true,

        state: {
            raw: null,
            size: {
                width: 0,
                height: 0
            },
            error: null
        },
        mutations: {
            setImage(state, {response, buffers}) {
                state.error = null;
                state.size.width = response.size[0];
                state.size.height = response.size[1];
                state.raw = buffers[0];
            },

            setError(state, error) {
                console.error("An error occured while fetching preview-data.", error);
                state.error = error.toString();
                state.size.width = 0;
                state.size.height = 0;
                state.raw = null;
            }
        }
    }
}


const createClipModule = function(model, type) {
    return {
        namespaced: true,
        modules: {
            image: createImageModule()
        },
        state: {
            length: 0,
            clip_id: null
        },
        mutations: {
            setLength(state, {response}) {
                state.length = response.length;
                state.clip_id = response.clip_id;
            }
        },
        actions: {
            async frame({commit}) {
                try {
                    const [response, buffers] = await model.requestFrame(type);
                    commit('image/setImage', {response, buffers});
                } catch (error) {
                    commit('image/setError', error);
                }
            },

            async length({commit}) {
                try {
                    const [response, buffers] = await model.requestLength(type);
                    commit('setLength', {response, buffers});
                } catch (error) {
                    commit('image/setError', error)
                }
            }
        }
    }
}

const createModelModule = function(model, binding) {
    return {
        namespaced: true,
        state: {
            clip: null,
            diff: null,

            frame: 0,
            zoom: 0
        },
        mutations: {
            sync(state, {key, value}) {
                state[key] = value;
            }
        }
    }
}

const createUpdateModule = function() {
    return {
        namespaced: true,
        state: {
            counter: 0
        },
        mutations: {
            updating(state) {
                state.counter += 1;
            },

            finished(state) {
                state.counter -= 1;
            }
        },
        actions: {
            async update({commit}, cb) {
                commit('updating');
                try {
                    return await cb();
                } finally {
                    commit('finished');
                }
            }
        }
    }
}

export default function makeStore(model) {
    const store = new Vuex.Store({
        modules: {
            clip:  createClipModule(model, 'clip'),
            diff:  createClipModule(model, 'diff'),
            model: createModelModule(model),
            updates: createUpdateModule(),
            modal: {
                namespaced: true,
                state: {
                    shown: false
                },
                mutations: {
                    show(state) {
                        state.shown = true;
                    },
                    hide(state) {
                        state.shown = false;
                    }
                },
                actions: {
                    toggle({commit, state}) {
                        if (state.shown) {
                            commit('hide');
                        } else {
                            commit('show');
                        }
                    }
                }
            }
        },

        getters: {
            updating(state) {
                return state.updates.counter > 0;
            },

            actualDiff(state) {
                return (!!state.model.diff)?state.diff:null
            },

            viewportSize(state) {
                let width = 0;
                let height = 0;

                if (!state.clip.image.error) {
                    width = state.clip.image.size.width;
                    height = state.clip.image.size.height;
                }

                if (!!state.model.diff && !state.diff.image.error) {
                    if (state.diff.image.size.width > width)
                        width = state.diff.image.size.width;
                    if (state.diff.image.size.height > height)
                        height = state.diff.image.size.height;
                }

                width = width * state.model.zoom / window.devicePixelRatio;
                height = height * state.model.zoom / window.devicePixelRatio;

                return {width, height};
            }
        },

        actions: {
            async fetchLengths({state, dispatch}) {
                await dispatch('updates/update', async () => {
                    const promises = [];
                    promises.push(dispatch('clip/length'));
                    if (!!state.model.diff)
                        promises.push(dispatch('diff/length'));
                    await Promise.all(promises);
                    promises.push(dispatch('fetchFrames'));
                });
            },

            async fetchFrames({state, dispatch}) {
                await dispatch('updates/update', async () => {
                    const promises = [];
                    promises.push(dispatch('clip/frame'));
                    if (!!state.model.diff)
                        promises.push(dispatch('diff/frame'));
                    await Promise.all(promises);
                });
            }
        }
    });
    model.bind(store, {namespace: 'model'});

    store.watch((state) => state.model.clip, () => store.dispatch('fetchLengths'));
    store.watch((state) => state.model.diff, () => store.dispatch('fetchLengths'));

    store.watch((state) => state.model.frame, () => store.dispatch('fetchFrames'));

    return store;
}
