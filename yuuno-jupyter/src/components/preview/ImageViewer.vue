<template>
    <div class="yuuno-image">
        <img :src="blobUrl" v-if="blobUrl && !image.error" :style="{width: `${size.width}px`, height: `${size.height}px`}">
        <div class="error" v-if="image.error">{{ image.error }}</div>
        <div class="no-data" v-if="!blobUrl && !image.error">
            <span class="character">Spoon-boy:</span> Do not try and bend the spoon. That's impossible. Instead... only try to realize the truth.<br />
            <span class="character">Neo:</span> What truth?<br />
            <span class="character">Spoon-boy:</span> There is no spoon.<br />
            <span class="character">Neo:</span> There is no spoon?<br />
            <span class="character">Spoon-boy:</span> Then you'll see, that it is not the spoon that bends, it is only yourself.
        </div>
    </div>
</template>

<style lang="less" scoped>
.yuuno-image {

    & > .no-data {
        background-color: #000000;
        color: #2f902f;
        font-family: 'Courier New', Courier, monospace;
        padding: 1em;
        min-width: 500px;

        & > .character {
            font-weight: bold;
            color: #00d400;
        }
    }
}
</style>


<script>
import { mapGetters, mapState } from 'vuex';
import FrameCache from '../../utils/FrameCache.js';
import ImageOperations from '../../utils/Images.js';

const cache = new FrameCache({max: 6});

export default {
    name: "ImageViewer",
    props: ['image', 'clip_id'],

    data() {
        return {
            blobUrl: null,
            ops: new ImageOperations()
        }
    },

    mounted() {
        this.rebuild(this.image);
    },

    destroyed() {
        this.ops.dispose();
    },

    methods: {
        async drawImage(img) {
            if (!!this.blobUrl) {
                const _url = this.blobUrl;
                this.$nextTick(() => URL.revokeObjectURL(_url));
                this.blobUrl = null;
            }

            this.blobUrl = URL.createObjectURL(new Blob([img]));
        },

        async rebuild(newValue) {
            const {clip_id, frame, zoom} = this;
            const {raw, error} = newValue;
            if (!!error) return;
            if (!!raw) {
                let img = raw;

                // Draw the image immediately. This way, we can immediately show the image as we receive it.
                this.drawImage(img);

                if (this.zoom != 1) {
                    img = await this.$store.dispatch('updates/update', async () => {
                        return await cache.get(`${clip_id}-${frame}-${zoom}`, async() => {
                            return await this.ops.resizeImage(
                                img,
                                this.image.size.width*this.zoom,
                                this.image.size.height*this.zoom
                            );
                        })
                    });

                    this.drawImage(img);
                };
            }
        }
    },

    computed: {
        ...mapState({
            zoom: (state) => state.model.zoom,
            frame: (state) => state.model.frame
        }),

        size() {
            return {
                width: this.image.size.width * this.zoom / window.devicePixelRatio,
                height: this.image.size.height * this.zoom / window.devicePixelRatio,
            }
        }
    },

    watch: {
        image: {
            handler(newValue) {
                this.rebuild(newValue);
            },
            deep: true
        },

        zoom(newValue) {
            this.rebuild(this.image);
        }
    }
}
</script>
