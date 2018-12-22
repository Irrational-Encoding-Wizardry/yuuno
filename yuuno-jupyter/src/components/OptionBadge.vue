<template>
    <div class="notification_widget btn btn-xs navbar-btn option-badge" disabled="disabled"><slot></slot></div>
</template>

<style lang="less" scoped>
.option-badge {
    cursor: unset;
    margin-top: 0;
}
</style>


<script>
export default {
    name: "OptionBadge"
}
</script>

