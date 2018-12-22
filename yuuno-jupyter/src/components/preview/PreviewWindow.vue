<template>
    <div class="preview">
        <preview-header></preview-header>
        <viewport :main="clip" :diff="diff" :method="diffMethod"></viewport>
        <options class="bottom">
            <input type="number" class="frame-no" v-model.lazy.number="frame" min="0" :max="clip.length" slot="left">
            <input type="range" class="frame-slide" v-model.lazy.number="frame" step="1" min="0" :max="clip.length">
            <select v-model.number="zoom" class="zoom-level" slot="right">
                <option :value="zoom" v-if="[0.25, 0.5, 1, 2, 3].indexOf(zoom) < 0">Custom</option>
                <option :value="0.25">25%</option>
                <option :value="0.50">50%</option>
                <option :value="1">100%</option>
                <option :value="2">200%</option>
                <option :value="3">300%</option>
            </select>
        </options>
    </div>
</template>

<script>
import {mapState} from 'vuex';
import {modelReadWrite} from '../../utils/VuexUtils';

import Options from '../Options';

import PreviewHeader from './Header';
import Viewport from './Viewport';
import MouseOverDiff from './diffs/MouseOverDiff';

export default {
    name: 'PreviewWindow',
    data() {
        return {diffMethod: MouseOverDiff}
    },

    components: {
        Options,
        PreviewHeader,

        Viewport
    },
    computed: {
        ...mapState({
            clip: (state) => state.clip,
        }),

        ...modelReadWrite({
            frame: (state) => state.model.frame,
            zoom: (state) => state.model.zoom
        }),

        diff() {
            return this.$store.getters.actualDiff
        }
    }

}
</script>

<style lang="less" scoped>
.preview {
    .frame-no {
        text-align: right;
        padding-left: 8px;
        background: transparent;
        border: 0;
    }
    .frame-slide {
        height: 100%;
    }
    .zoom-level {
        background: transparent;
        border: 0;
        padding-right: 8px;
    }
}
</style>

