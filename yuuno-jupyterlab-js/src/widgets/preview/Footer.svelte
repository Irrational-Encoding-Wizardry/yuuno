<div class="bottom">
    <div class="current-frame">
        {#if proposedValue === null}
            <input bind:value={ frame } type="number">
        {:else}
            <input bind:value={ proposedValue } type="number">
        {/if}
        /
        { length }
    </div>
    <div class="line-slider">
        <LineSlider bind:value={ frame } bind:proposedValue={ proposedValue } min={0} max={ length } />
    </div>
    <div class="zoom">
        <JupyterSelect bind:value={ zoom }>
            <option value={.25}>25%</option>
            <option value={.50}>50%</option>
            <option value={.70}>75%</option>

            <option value={1}>100%</option>

            <option value={1.5}>150%</option>
            <option value={2.0}>200%</option>
            <option value={3.0}>300%</option>
        </JupyterSelect>
    </div>
</div>

<style>
    .bottom {
        display: flex;
    }

    .current-frame {
        line-height: 100%;
        padding-top: 4px;
        padding-right: 5px;
    }

    .current-frame > input {
        border: 0;
        width: 50px;
        text-align: right;
        background: transparent;
        color: var(--jp-widgets-color);
    }

    .line-slider {
        flex-grow: 1;
        flex-shrink: 1;
    }
</style>

<script>
    export let frame;
    export let length;
    export let zoom;

    import LineSlider from "./LineSlider.svelte";
    import JupyterSelect from "./JupyterSelect.svelte";

    let proposedValue;
</script>
