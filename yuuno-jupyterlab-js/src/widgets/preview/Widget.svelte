
{#await currentPreview}
    <div>Loading ...</div>
{:then length}
    <div class="preview">
        <div class="header">
            <Header clips={clips} bind:clip_id={ $clip_id } bind:diff_id={ $diff_id } rpc={ preview } frame={ $frame } />
        </div>
        <div class="viewport">
            <Viewport clips={clips} clip_id={ $clip_id } diff_id={ $diff_id } rpc={ preview } frame={ $frame } zoom={ $zoom } />
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

    const raw_clips = model_attribute(component, "clips");

    const clip_id = model_attribute(component, "clip");
    const diff_id = model_attribute(component, "diff");

    const debouncedFrame = debounce(100, frame);

    const preview = getRPCForModel(component);
    preview.open();
    onDestroy(() => preview.close());

    $: clips = $raw_clips !== null ? $raw_clips : {};

    function redistribute(_, __, ___) {
        const keys = Object.keys(clips);
        keys.sort();

        if (keys.length == 1) {
            $clip_id = keys[0];
            $diff_id = null;
        } else if (keys.length == 2) {
            $clip_id = keys[0];
            $diff_id = keys[1];
        } else {
            if (keys.indexOf($clip_id) === -1)
                $clip_id = keys[0];

            if ($diff_id !== null && keys.indexOf($diff_id) === -1)
                $diff_id = null;

            if ($clip_id === $diff_id)
                $diff_id = null;
        }
    }
    $: redistribute(clips, $clip_id, $diff_id);
    $: currentPreview = [clips, $clip_id, $diff_id, preview.length()][3];
</script>
