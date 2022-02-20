<div class="top">
    {#if clipCount === 0}
        <div>No image</div>
    {:else if clipCount == 1}
        {#await frameDataPromiseLeft}
            <div>Updating ...</div>
        {:then frameData}
            <div>{ frameData.size[0] }px &times; { frameData.size[1] }px</div>
            <div>
                <Props props={ frameData.props }/>
            </div>

        {:catch}
            <div>Error</div>
        {/await}

        <div class="spacer" />

        <div>
            <button class="toolbar" on:click={((ty) => () => download(ty))('clip')}>
                <JupyterIcon icon="download" />
            </button>
        </div>

    {:else}
        <!-- MAIN -->
        <div>
            {#if clipCount > 2}
                <JupyterSelect bind:value={ clip_id }>
                    {#each clipIds as id (id)}
                        <option value={ id }>{ id }</option>
                    {/each}
                </JupyterSelect>
            {:else}
                <span>{ clip_id }</span>
            {/if}
        </div>

        {#await frameDataPromiseLeft}
            <div>Updating ...</div>
        {:then frameData}
            <div>{ frameData.size[0] }px &times; { frameData.size[1] }px</div>
            <div>
                <Props props={ frameData.props }/>
            </div>
        {:catch}
            <div>Error</div>
        {/await}

        <div>
            <button class="toolbar" on:click={((ty) => () => download(ty))('clip')}>
                <JupyterIcon icon="download" />
            </button>
        </div>

        <!-- CENTER -->

        <div class="spacer" />

        <!-- COMPARISON -->
        {#if diff_id !== null}
            <div>
                <button class="toolbar" on:click={((ty) => () => download(ty))('diff')}>
                    <JupyterIcon icon="download" />
                </button>
            </div>

            {#await frameDataPromiseRight}
                <div>Updating ...</div>
            {:then frameData}
                <div>
                    <Props props={ frameData.props }/>
                </div>
                <div>{ frameData.size[0] }px &times; { frameData.size[1] }px</div>
            {:catch}
                <div>Error</div>
            {/await}
        {/if}

        <div>
            {#if clipCount > 2}
                <JupyterSelect bind:value={ diff_id }>
                    <option value={null}>- None -</option>
                    {#each clipIds as id (id)}
                        <option value={ id }>{ id }</option>
                    {/each}
                </JupyterSelect>
            {:else}
                <span>{ diff_id }</span>
            {/if}
        </div>

    {/if}
</div>

<style>
    .top {
        display: flex;
        line-height: 27px;
        height: 27px;
    }

    .top > *:not(.spacer) {
        padding: 0px 10px;
    }

    .top > *:not(:last-child) {
        border-right: var(--jp-border-width) solid var(--jp-cell-editor-border-color);
    }

    .spacer {
        flex-grow: 1;
        flex-shrink: 1;
    }

    .toolbar {
        border: 0;
        background: transparent;
        margin: 0;
        padding: 0;
        line-height: 35px;
    }

    .toolbar:not(:last-child) {
        padding-right: 5px;
    }
</style>

<script>
    export let rpc;
    export let frame;

    export let clip_id;
    export let diff_id;  // Should always be null.

    export let clips;

    import JupyterSelect from "./JupyterSelect.svelte";
    import JupyterIcon from "../../components/JupyterIcon.svelte";
    import Props from "./Props.svelte";

    import { tick } from "svelte";
    $: lengthPromise = [diff_id, clip_id, rpc.length()][2];

    $: clipIds = Object.keys(clips);
    $: clipCount = clipIds.length;

    $: frameDataPromiseLeft = [diff_id, clip_id, rpc.frame({ frame })][2];
    $: frameDataPromiseRight = [diff_id, clip_id, rpc.frame({ frame, image: "diff" })][2];

    async function download(type) {
        const rawFrame = await rpc.frame({ frame, image: type });
        const blob = URL.createObjectURL(new Blob([rawFrame.buffers[0]], { type: 'image/png' }));
        const a = document.createElement("a");
        document.body.append(a);
        a.href = blob;
        a.download = `Image-${type}-${frame}.png`;
        a.click();
        await tick();
        URL.revokeObjectURL(blob);
        a.remove();
    }
</script>
