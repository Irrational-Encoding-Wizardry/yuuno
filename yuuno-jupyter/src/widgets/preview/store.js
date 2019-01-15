import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);


const createImageModule = function() {
    return {
        namespaced: true,

        state: {
            raw: null,
            metadata: {},
            format: null,
            size: {
                width: 0,
                height: 0
            },
            error: null
        },
        mutations: {
            setMetadata(state, {response, buffers}) {
                state.metadata = response;
            },

            setFormat(state, {response, buffers}) {
                state.format = [
                    ['Grayscale', 'RGB', 'YUV'][response[2]],
                    response[0],
                    ['Integer', 'Float'][response[3]],
                    response[5],
                    response[4]
                ];
            },

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
            clip_id: null,
            metadata: {}
        },
        mutations: {
            setLength(state, {response}) {
                state.length = response.length;
                state.clip_id = response.clip_id;
            },

            setMetadata(state, {response}) {
                state.metadata = response;
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

            async metadata({commit}) {
                try {
                    const [response, buffers] = await model.requestMeta(type);
                    commit('image/setMetadata', {response, buffers});
                } catch (error) {
                    commit('image/setError', error);
                }
            },

            async clipMetadata({commit}) {
                try {
                    const [response, buffers] = await model.requestClipMeta(type);
                    commit('setMetadata', {response, buffers});
                } catch (error) {
                    commit('image/setError', error);
                }
            },

            async format({commit}) {
                try {
                    const [response, buffers] = await model.requestFormat(type);
                    commit('image/setFormat', {response, buffers});
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
                const _rqData = function(p, type) {
                    p.push(dispatch(`${type}/length`));
                    p.push(dispatch(`${type}/clipMetadata`));
                };

                await dispatch('updates/update', async () => {
                    const promises = [];
                    _rqData(promises, 'clip');
                    if (!!state.model.diff)
                        _rqData(promises, 'diff');
                    await Promise.all(promises);
                    promises.push(dispatch('fetchFrames'));
                });
            },

            async fetchFrames({state, dispatch}) {
                const _rqData = function(p, type) {
                    p.push(dispatch(`${type}/frame`));
                    p.push(dispatch(`${type}/metadata`));
                    p.push(dispatch(`${type}/format`));
                };

                await dispatch('updates/update', async () => {
                    const promises = [];
                    _rqData(promises, 'clip');
                    if (!!state.model.diff) {
                        _rqData(promises, 'diff');
                    }
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
