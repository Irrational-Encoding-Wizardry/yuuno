<template>
    <div class="options-yuuno navbar navbar-default">
        <div class="left"><slot name="left"></slot></div>
        <div class="spacer"><slot></slot></div>
        <div class="right"><slot name="right"></slot></div>
    </div>
</template>

<style lang="less" scoped>

.options-yuuno {
    display: flex;
    justify-content: space-between;

    margin-bottom: 0;
    border-radius: 5px;

    &.top {
        border-bottom-left-radius: 0;
        border-bottom-right-radius: 0;
        border-bottom: 0;
    }
    &.bottom {
        border-top-left-radius: 0;
        border-top-right-radius: 0;
        border-top: 0;
    }
    &.inner {
        border-radius: 0;
        border-top: 0;
        border-bottom: 0;
    }
    border-radius: 5px;
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

    .navbar-btn {
        margin-right: 0;
        margin-top: 0;
    }
}
</style>
