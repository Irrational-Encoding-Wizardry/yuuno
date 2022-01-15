<div class="progress">
    <div class="past" style="width: { percPast * 100 }%;"></div>
</div>

<style>
    .progress {
        display: block;

        border-left: var(--jp-border-width) solid var(--jp-cell-editor-border-color);
        border-right: var(--jp-border-width) solid var(--jp-cell-editor-border-color);
    }

    .progress > * {
        position: absolute;
        height: 2px;
        top: 0;
    }

    .past {
        left: 0;
        background-color:  var(--jp-brand-color1);
    }
</style>

<script>
    export let value = 0;
    export let max = 100;
    export let min = 0;

    $: span = max - min;
    $: percPast = (value - min) / span;
</script>

