<style lang="less" scoped>
.bubble-tooltip {
    position: relative;
    display: inline-block;

    & > .bubble-target {
        border-bottom: 1px dotted black;
    }

    & > .bubble {
        @padding: 0px;
        @width: 300px;
        @height: 350px;
        @background: rgb(221, 221, 221);
        @foreground: black;
        @border: darken(@background, 20%);
        @radius: 6px;

        visibility: hidden;
        width: @width;
        background-color: @background;
        color: @foreground;
        text-align: center;
        padding: @padding 0;
        border-radius: @radius;
        border: 1px solid @border;
        
        /* Position the tooltip text - see examples below! */
        position: absolute;
        z-index: 1;

        & > .bubble-content {
            border-radius: @radius;
        
            max-height: @height;
            overflow: auto;
        }

        &::after {
            content: " ";
            position: absolute;

            border-width: 5px;
            border-style: solid;
            border-color: transparent;
        }

        &.left {
            top: -@padding;
            left: 105%; 

            &::after {
                top: 50%;
                left: 100%; /* To the right of the tooltip */
                margin-top: -5px;
                border-left-color: @border;
            }
        }
        &.right {
            top: -@padding;
            right: 105%; 

            &::after {
                top: 50%;
                right: 100%; /* To the left of the tooltip */
                margin-top: -5px;
                border-right-color: @border;
            }
        }
        &.top {
            width: @width;
            bottom: 100%;
            left: 50%; 
            margin-left: -@width/2; /* Use half of the width (120/2 = 60), to center the tooltip */

            &::after {
                top: 50%;
                right: 100%; /* To the left of the tooltip */
                margin-top: -5px;
                border-top-color: @border;
            }
        }
        &.bottom {
            width: @width;
            top: 100%;
            left: 50%; 
            margin-left: -@width/2; /* Use half of the width (120/2 = 60), to center the tooltip */

            &::after {
                bottom: 100%;  /* At the top of the tooltip */
                left: 50%;
                margin-left: -5px;
                border-bottom-color: @border;
            }
        }
    }

    &:hover > .bubble {
        visibility: visible;
    }
}
</style>

<template>
    <div class="bubble-tooltip">
        <span class="bubble-target">
            <slot name="text"></slot>
        </span>
        <div class="bubble" :class="[position]">
            <div class="bubble-content">
                <slot name="bubble"></slot>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Tooltip',
    props: ['position']
}
</script>

