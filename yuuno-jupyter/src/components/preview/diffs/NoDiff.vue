<template>
    <div class="viewport--no-diff">
        <slot name="main"></slot>
        <div style="display: none;">
            <slot name="diff"></slot>
        </div>
    </div>
</template>

<script>
export default {
    name: 'NoDiff'
}
</script>
