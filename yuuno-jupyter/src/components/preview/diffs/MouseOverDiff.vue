<template>
    <div class="viewport--mouse-over" :style="targetSize">
        <div class="main">
            <slot name="main"></slot>
        </div>
        <div class="diff">
            <slot name="diff"></slot>
        </div>
    </div>
</template>

<script>
export default {
    name: 'MouseOverDiff',

    computed: {
        targetSize() {
            const {width, height} = this.$store.getters.viewportSize;
            return {width: `${width}px`, height: `${height}px`};
        }
    }
}
</script>


<style lang="less" scoped>
.viewport--mouse-over {
    position: relative;
    width: 100%;
    height: 100%;

    .main, .diff {
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }

    &:hover {
        .main {
            display: none;
        }
        .diff {
            display: block;
        }
    }

    &:not(:hover) {
        .main {
            display: inline;
        }
        .diff {
            display: none;
        }
    }
}
</style>

