<template>
    <div class="yuuno--modal--base">
        <div class="yuuno--modal--background"></div>
        <div class="yuuno--modal--content">
            <div class="yuuno--modal--wrapper">
                <slot></slot>
            </div>
        </div>
    </div>
</template>

<style lang="less" scoped>
.yuuno--modal--base {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 1001;

    & > .yuuno--modal--background {
        position: absolute;
        top: 0;
        left: 0;

        width: 100vw;
        height: 100vh;

        background: rgba(0, 0, 0, 0.5);
    }

    & > .yuuno--modal--content {
        position: absolute;
        top: 0;
        left: 0;
        z-index: 1;

        display: flex;
        width: 100vw;
        height: 100vh;

        justify-content: space-around;
        align-items: center;

        & > .yuuno--modal--wrapper {
            display: flex;

            overflow: auto;

            width: 90vw;
            height: 90vh;

            & > * {
                flex-grow: 1;
                flex-shrink: 1;
            }
        }
    }
}
</style>

<script>
export default {
    name:  'Modal'
}
</script>
