<template>
    <div class="yuuno-viewport" :class="{'modalized': inModal}" v-dragscroll>
        <div class="scroll-area" :style="targetSize">
            <component :is="actualMethod">
                <template slot="main">
                    <image-viewer :image="main.image" :clip_id="main.clip_id"></image-viewer>
                </template>
                <template slot="diff" v-if="!!diff">
                    <image-viewer :image="diff.image" :clip_id="diff.clip_id"></image-viewer>
                </template>
            </component>
        </div>
    </div>
</template>

<style lang="less" scoped>
.yuuno-viewport {
    max-height: 500px;
    min-height: 500px;
    &.modalized {
        height: 80vh;
        max-height: unset;
        min-height: unset;
    }
    position: relative;
    overflow: auto;

    & > .scroll-area {
        position: absolute;
        top: 0;
        left: 0;
    }

    // Source: https://stackoverflow.com/questions/35361986/css-gradient-checkerboard-pattern
    background: linear-gradient(45deg, #808080 25%, transparent 25%),
                linear-gradient(-45deg, #808080 25%, transparent 25%),
                linear-gradient(45deg, transparent 75%, #808080 75%),
                linear-gradient(-45deg, transparent 75%, #808080 75%);
    background-size: 20px 20px;
    background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
    background-color: white;
}
</style>


<script>
import NoDiff from './diffs/NoDiff';
import ImageViewer from './ImageViewer';
import {dragscroll} from 'vue-dragscroll';
import { mapState } from 'vuex';

export default {
    name: 'Viewport',
    props: ['main', 'diff', 'method'],

    components: {
        ImageViewer
    },

    directives: {
        dragscroll
    },

    computed: {
        actualMethod() {
            if (!this.diff) return NoDiff;
            return this.method;
        },

        targetSize() {
            const {width, height} = this.$store.getters.viewportSize;
            return {width: `${width}px`, height: `${height}px`};
        },

        ...mapState({
            inModal: (state) => state.modal.shown
        })
    }
}
</script>

