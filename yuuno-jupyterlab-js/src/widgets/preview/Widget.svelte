
{#await currentPreview}
    <div>Loading ...</div>
{:then length}
    <div class="preview">
        <div class="header">
            <Header clip_id={ $clip_id } diff_id={ $diff_id } rpc={ preview } frame={ $frame } />
        </div>
        <div class="viewport">
            <Viewport clip_id={ $clip_id } diff_id={ $diff_id } rpc={ preview } frame={ $frame } zoom={ $zoom } />
        </div>
        <div class="footer">
            <Footer bind:frame={ $frame } bind:zoom={ $zoom } length={ length.length } />
        </div>
    </div>
{/await}

<style>
    .preview {
        border: var(--jp-border-width) solid var(--jp-cell-editor-border-color);
        border-radius: 0px;
        background: var(--jp-cell-editor-background);
        
        display: flex;
        flex-direction: column;
    }

    .preview > * {
        width: 100%;
    }

    .viewport {
        min-height: 640px;

        flex-grow: 1;
        flex-shrink: 1;

        display: flex;
        flex-direction: column;
    }
</style>

<script>
    export let component;

    import Header from "./Header.svelte";
    import Viewport from "./Viewport.svelte";
    import Footer from "./Footer.svelte";

    import { model_attribute, debounce } from "../../utils";
    import { getRPCForModel } from "./rpc";
    import { onDestroy } from 'svelte';

    const frame = model_attribute(component, "frame");
    const zoom = model_attribute(component, "zoom");

    const clip_id = model_attribute(component, "clip");
    const diff_id = model_attribute(component, "diff");

    const debouncedFrame = debounce(100, frame);

    const preview = getRPCForModel(component);
    preview.open();
    onDestroy(() => preview.close());

    $: currentPreview = [$clip_id, $diff_id, preview.length()][2];
    $: console.log(component);
</script>
