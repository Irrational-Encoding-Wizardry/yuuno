<div class="line-slider" on:mouseenter={enter} on:mouseleave={leave} on:mousemove={move} on:click={submit} bind:this={myself}>
    <div class="past" style="width: { percPast * 100 }%;"></div>
    {#if proposedValue === null}
        <div class="select" style="left: { percPast * 100 }%;"></div>
    {:else}
        <div class="proposed" style="left: { proposedPerc * 100}%;"></div>
    {/if}
    <div class="future" style="width: { percFuture * 100 }%;"></div>
</div>

<style>
    .line-slider {
        position: relative;
        width: 100%;
        height: 100%;
        display: block;

        border-left: var(--jp-border-width) solid var(--jp-cell-editor-border-color);
        border-right: var(--jp-border-width) solid var(--jp-cell-editor-border-color);
    }

    .line-slider > * {
        position: absolute;
        height: 20%;
        bottom: 0;
    }

    .past {
        left: 0;
        background-color:  var(--jp-brand-color1);
    }

    .future {
        right: 0;
        background-color: var(--jp-cell-editor-border-color);
    }

    .select, .proposed {
        height: 100%;
        top: 0;
        width: var(--jp-border-width);
        background-color: var(--jp-brand-color1);
    }
</style>

<script>
    export let value = 0;
    export let max = 100;
    export let min = 0;

    export let proposedValue = null;
    export let proposedPerc = null;

    let myself;

    function enter(event) {
        proposedValue = min;
        move(event);
    }

    function leave() {
        proposedValue = null;
    }

    function move(event) {
        const { pageX, pageY } = event;
        const { left, top, right } = myself.getBoundingClientRect();

        const width = right - left;
        const vX = pageX - left;

        proposedPerc = vX / width;
        const rawProposal = (proposedPerc * span) + min;
        proposedValue = Math.round(rawProposal);
    }

    function submit() {
        value = proposedValue;
    }
    
    $: span = max - min;
    $: percPast = (value - min) / span;
    $: percFuture = 1 - percPast;
</script>

