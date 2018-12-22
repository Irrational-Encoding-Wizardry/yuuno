<template>
    <div>   
        <template v-if="!!diff">
            <options class="top">
                <template slot="left">
                    <option-group>Comparing</option-group>
                </template>
                <template slot="right">
                    <option-group v-if="updating">
                        <option-badge>Updating</option-badge>
                    </option-group>
                    <option-group class="no-border">
                        <div class="btn-group">
                            <button class="navbar-btn btn btn-xs" @click="toggleModal"><i class="fa fa-window-maximize"></i></button>
                        </div>
                    </option-group>
                </template>
            </options>
            <options class="inner">
                <template slot="left">
                    <option-group>
                        <option-badge>Main</option-badge>
                    </option-group>
                    <template v-if="clipId !== null">
                        <option-group class="no-border">
                            {{ clip.length }} frames
                        </option-group>
                        <option-group>
                            {{ clip.image.size.width }}x{{ clip.image.size.height }}
                        </option-group>
                        <option-group class="no-border">
                            <div class="btn-group">
                                <button class="navbar-btn btn btn-xs" @click="download(clip, 'clip')"><i class="fa fa-download"></i></button>
                            </div>
                        </option-group>
                    </template>
                    <template v-else>
                        <option-group>
                            <option-badge class="warning">No Image</option-badge>
                        </option-group>
                    </template>
                </template>
                <template slot="right">
                    <option-group>
                        <div class="btn-group">
                            <button class="navbar-btn btn btn-xs" @click="download(diff, 'comparison')"><i class="fa fa-download"></i></button>
                        </div>
                    </option-group>
                    <option-group class="no-border">
                        {{ diff.length }} frames
                    </option-group>
                    <option-group>
                        {{ diff.image.size.width }}x{{ diff.image.size.height }}
                    </option-group>
                    <option-group class="no-border">
                        <option-badge>Comparison</option-badge>
                    </option-group>
                </template>
            </options>
        </template>
        <template v-else>
            <options class="top">
                <template slot="left" v-if="clipId !== null">
                    <option-group>
                        {{ clip.length }} frames
                    </option-group>
                    <option-group>
                        {{ clip.image.size.width }}x{{ clip.image.size.height }}
                    </option-group>
                </template>
                <template slot="left" v-else>
                    <option-group>
                        <option-badge class="warning">No image</option-badge>
                    </option-group>
                </template>
                <template slot="right">
                    <option-group v-if="updating">
                        <option-badge>Updating</option-badge>
                    </option-group>
                    <option-group class="no-border">
                        <div class="btn-group">
                            <button class="navbar-btn btn btn-xs" @click="download(clip, 'clip')" v-if="clipId !== null"><i class="fa fa-download"></i></button>
                            <button class="navbar-btn btn btn-xs" @click="toggleModal"><i class="fa fa-window-maximize"></i></button>
                        </div>
                    </option-group>
                </template>
            </options>
        </template>
    </div>
</template>

<script>
import Options from '../Options';
import OptionGroup from '../OptionGroup';
import OptionBadge from '../OptionBadge';
import { mapState, mapGetters, mapActions } from 'vuex';
import { createMountedElement } from '../../utils/DOMUtils';

export default {
    name: "Header",
    components: {
        Options,
        OptionGroup,
        OptionBadge
        },

    computed: {
        ...mapState({
            clip: (state) => state.clip,
            inModal: (state) => state.modal.shown,
            frame: (state) => state.model.frame,
            
            clipId: (state) => state.model.clip,
            diffId: (state) => state.model.diff
        }),

        ...mapGetters({
            diff: 'actualDiff',
            updating: 'updating'
        }),
    },

    methods: {
        ...mapActions({
            toggleModal: 'modal/toggle'
        }),

        download(img, type) {
            if (img.error) return;
            const a = createMountedElement(document.body, "a");
            const url = URL.createObjectURL(new Blob([img.image.raw], {type: 'image/png'}));
            a.href = url;
            a.download = `Image-${type}-${this.frame}.png`
            a.click();
            URL.revokeObjectURL(url);
        }
    }
}
</script>
