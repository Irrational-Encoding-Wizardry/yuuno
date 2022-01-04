<div class="viewport" on:mouseenter={enter} on:mouseleave={leave} on:mousedown|capture|stopPropagation|preventDefault={down} on:mouseup|capture|stopPropagation|preventDefault={up} on:mousemove={move} bind:this={myself} >
    <div class="zero-sizer {mode}">
        {#if clip_id !== null}
            <div class="item main">
                <Image rpc={ rpc } frame={ frame } zoom={ zoom } type="clip" />
            </div>
        {/if}

        {#if diff_id !== null}
            <div class="item diff">
                <Image rpc={ rpc } frame={ frame } zoom={ zoom } type="diff" />
            </div>
        {/if}
    </div>
</div>

<style>
    .viewport {
        display: flex;
        flex-grow: 1;
        flex-shrink: 1;

        background-image:
            linear-gradient(45deg, #808080 25%, transparent 25%),
            linear-gradient(-45deg, #808080 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, #808080 75%),
            linear-gradient(-45deg, transparent 75%, #808080 75%);
        background-size: 20px 20px;
        background-position: 0 0, 0 10px, 10px -10px, -10px 0px;

        overflow: auto;
    }

    .zero-sizer {
        position: relative;
        width: 0;
        height: 0;
    }

    .zero-sizer > .item {
        position: absolute;
        top: 0;
        left: 0;
    }

    .item.main, .item.diff {
        display: none;
    }

    .main > .item.main {
        display: block;
    }

    .diff > .item.diff {
        display: block;
    }
</style>

<script>
    import Image from "./Image.svelte";

    export let rpc;
    export let frame;
    export let zoom = 1;

    export let clip_id, diff_id;

    let myself;

    let entered = false;

    $: single_clip = (clip_id === null) != (diff_id === null);
    $: single_clip_mode = clip_id !== null ? "main" : "diff";
    $: multi_clip_mode = entered ? "diff": "main";
    $: mode = single_clip ? single_clip_mode : multi_clip_mode;

    function enter() {
        entered = true;
    }

    function leave() {
        entered = false;
    }


    let panning = null;

    function down(event) {
        panning = [
            event.screenX,
            event.screenY,
            myself.scrollLeft,
            myself.scrollTop,
        ];
    }

    function up() {
        panning = null;
    }

    function move(event) {
        if (panning === null) return;

        const { screenX, screenY } = event;
        const [ startX, startY, scrollLeft, scrollTop] = panning;

        const dX = startX - screenX;
        const dY = startY - screenY;

        myself.scrollLeft = scrollLeft + dX;
        myself.scrollTop = scrollTop + dY;
    }
</script>
