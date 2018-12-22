<template>
    <div class="info-group">
        <slot></slot>
    </div>
</template>

<style lang="less" scoped>
.info-group {
    padding-left: 0.5em;
    padding-right: 0.5em;

    line-height: 30px;

    border-left: 1px solid #ccc;
    &:first-child,&.no-border {
        border-left: 0;
    }

    & > .btn-group {
        & > .btn {
            margin-top: 0;
        }
        margin-top: 0;
    }
}
</style>


<script>
export default {
    name: "OptionGroup"
}
</script>

