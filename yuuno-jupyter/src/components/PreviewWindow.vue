<template>
  <div class="preview-window">
      <div class="navbar navbar-default info">
        <div class="left">
          <span class="info-group">
              {{ length }} frames
          </span>
          <span class="info-group" :title="`Displayed as ${display_size.width}x${display_size.height}`" v-if="!error">
              {{ size.width }}x{{ size.height }}
          </span>
          <span class="info-group" v-if="zoom != 1 && !error">
              {{ size.width*zoom }}x{{ size.height*zoom }} (zoomed)
          </span>
        </div>
        <div class="spacer"></div>
        <div class="right">
          <span class="info-group" v-if="!!error">
              <span class="notification_widget btn btn-xs navbar-btn" disabled="disabled">Error</span>
          </span>
          <span class="info-group" v-if="updating">
              <span class="notification_widget btn btn-xs navbar-btn" disabled="disabled">Updating</span>
          </span>
          <span class="info-group">
              <div class="btn-group">
                  <button class="navbar-btn btn btn-xs" @click="download" v-if="!error"><i class="fa fa-download"></button>
              </div>
              <div class="btn-group">
                  <button class="navbar-btn btn btn-xs" @click="toggleModal"><i class="fa" :class="[in_modal?'fa-window-restore':'fa-window-maximize']"></button>
              </div>
          </span>
        </div>
      </div>
      <image-view class="image" :style="{minHeight: `${size.height>400?400:size.height}px`}" v-if="!error"></image-view>
      <code class="error" v-if="!!error">{{ error }}</code>
      <div class="navbar navbar-default bottom-bar">
        <input class="bottom-bar--frame-no" v-model.number="frame" :max="length-1" type="number">
        <input class="bottom-bar--frame-slide" v-model.number="frame" type="range" min="0" :max="length-1">
        <select v-model.number="zoom" class="bottom-bar--zoom-level">
            <option :value="zoom" v-if="[0.25,0.50,1,2,3,4].indexOf(zoom) < 0">Custom</option>
            <option :value="0.25">25%</option>
            <option :value="0.50">50%</option>
            <!-- <option :value="0.75">75%</option> -->
            <option :value="1">100%</option>
            <!-- <option :value="1.25">125%</option> -->
            <!-- <option :value="1.50">150%</option> -->
            <option :value="2">200%</option>
            <option :value="3">300%</option>
            <option :value="4">400%</option>
        </select>
      </div>
  </div>
</template>

<style lang="less" scoped>
.preview-window {
    display: flex;
    flex-direction: column;

    & > .info {
        display: flex;
        justify-content: space-between;

        margin-bottom: 0;
        border-radius: 0;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        border-bottom: 0;
        padding-left: 3px;
        padding-right: 3px;
        
        & > .spacer {
            flex-grow: 1;
            flex-shrink: 1;
        }

        & > .left, & > .right {
            display: flex;
            height: 30px;
            
            flex-grow: 0;
            flex-shrink: 0;
        }

        & > .left > .info-group, & > .right > .info-group {
            &:last-child {
                border-right: 0 !important;
                padding-right: 0 !important;
            }

            display: inline-block;
            height: 30px;
            line-height: 30px;
            padding-left: 10px;
            padding-right: 10px;
            border-right: 1px solid #e7e7e7;

            & > .btn-group > .btn {
                padding: 2px 8px;
            }
        }
    }

    & > .image {
        flex-grow: 1;
        flex-shrink: 1;
    }

    & > .error {
        color: #faa;
        background: #330101;
    }

    .navbar-btn {
        margin-right: 0;
        margin-top: 0;
    }

    & > .bottom-bar {
        display: flex;
        flex-direction: row;
        flex-grow: 0;
        flex-shrink: 1;

        border-radius: 0;
        border-bottom-left-radius: 5px;
        border-bottom-right-radius: 5px;
        border-top: 0;

        & > .bottom-bar--frame-no {
            flex-grow: 0;
            flex-shrink: 0;

            max-width: 5em;

            background: transparent;
            border: 0;
            text-align: right;
            padding-left: 8px;
        }

        & > .bottom-bar--frame-slide {
            flex-grow: 1;
            flex-shrink: 1;
        }

        & > .bottom-bar--zoom-level {
            flex-grow: 0;
            flex-shrink: 0;
            background: transparent;
            border: 0;
            padding-right: 8px;
        }
    }
}
</style>


<script>
import {mapState} from 'vuex';
import {modelReadWrite} from '../utils/vuexUtils';

import ImageDisplay from './ImageDisplay';

export default {
    name: "PreviewWidget",

    components: {
        'image-view': ImageDisplay
    },

    computed: {
        ...modelReadWrite({
            clip: state => state.model.clip,
            frame: state => state.model.frame,
            zoom: state => state.model.zoom
        }),

        ...mapState({
            length: state => state.length,
            size: state => state.image.size,
            updating: state => state.updating,

            error: state => state.error,

            in_modal: state => state.in_modal
        }),

        display_size() {
            return {
                width: Math.round(this.size.width * this.zoom / window.devicePixelRatio),
                height: Math.round(this.size.height * this.zoom / window.devicePixelRatio)
            }
        }
    },

    methods: {
        download() {
            this.$store.dispatch('downloadImage');
        },

        toggleModal() {
            this.$store.dispatch('toggleModal');
        }
    },

    watch: {
        async clip() {
            await this.$store.dispatch('computeLength');
            await this.$store.dispatch('renderFrame');
        },

        async frame() {
            await this.$store.dispatch('renderFrame');
        }
    }
}
</script>
