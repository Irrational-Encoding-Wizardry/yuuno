<template>
    <div class="viewport" :style="{minHeight: `${(250<display_size.height)?250:display_size.height}px`}" v-dragscroll>
        <div class="pan-port" :style="{width: `${display_size.width}px`, height: `${display_size.height}px`}">
            <img :src="image_blob" :width="display_size.width" :height="display_size.height" />
        </div>
    </div>
</template>

<style lang="less" scoped>
.viewport {
    background: #444;

    position: relative;
    overflow-x: auto;
    overflow-y: auto;
    width: 100%;
    height: auto;

    & > .pan-port {
        position: absolute;
        top: 0;
        left: 0;
    }
}
</style>


<script>
import {mapState} from 'vuex';
import {dragscroll} from 'vue-dragscroll';

import FrameCache from '../utils/frameCache';

const nextTick = require('next-tick');
const frameCache = new FrameCache(5);

import JIMP from 'jimp/es';

export default {
    name: "ImageDisplay",
    directives: {
        dragscroll
    },

    data() {
        return {
            'image_blob': null,
            'image_buffer': null
        }
    },

    beforeDestroy() {
        this.disposeBlob();
    },

    computed: {
        ...mapState({
            image: (state) => state.image.raw,
            zoom: (state) => state.model.zoom,

            size: (state) => state.image.size,
            in_modal: (state) => state.in_modal
        }),

        actual_size() {
            return {
                width: this.size.width * this.zoom,
                height: this.size.height * this.zoom
            }
        },

        display_size() {
            return {
                width: this.size.width * this.zoom / window.devicePixelRatio,
                height: this.size.height * this.zoom / window.devicePixelRatio
            }
        }
    },

    async beforeMount() {
        await this.refresh_image();
    },

    methods: {
        disposeBlob() {
            if (this.image_blob != null)
                URL.revokeObjectURL(this.image_blob);
            this.image_blob = null;
            this.image_buffer = null;
        },

        async _updateImage(image) {
            const {clip, frame, zoom} = this.$store.state.model;
            return (await frameCache.get(`${clip}--${frame}--${zoom}`, async() => {
                let img = await JIMP.read(image.buffer);
                let render = await img.resize(this.size.width*zoom, this.size.height*zoom, JIMP.RESIZE_NEAREST_NEIGHBOR).getBufferAsync(JIMP.MIME_PNG);
                return render;
            }));
        },

        async updateImage(image, zoom) {
            if (image === null) return this.disposeBlob();
            await this.$store.dispatch('update', async () => {
                if (this.zoom != 1) {
                    image = await this._updateImage(image);
                }
                this.disposeBlob();
                this.image_buffer = new Blob([image]);
            });
            await this.refresh_image();
        },

        async refresh_image() {
            if (this.image_buffer == null)
                return (await this.updateImage(this.image, this.zoom));

            this.image_blob = URL.createObjectURL(new Blob([this.image_buffer]));
        }
    },

    watch: {
        image(newValue) {
            this.updateImage(newValue, this.zoom);
        },

        zoom(newValue) {
            this.updateImage(this.image, newValue);
        },
    }
}
</script>

