<div class="audio">
    <div class="meta">
        { displayTime }
    </div>
    <div class="slider">
        <BufferSlider bind:value={playhead} buffered={loaded} samples={samples} max={sample_count} bind:proposedValue={ proposed } on:update={ seek } />
    </div>
    <div class="">
        {#if playing}
            <button class="toolbar" on:click={() => { player.pause(); }} bind:this={pauseBtn} />
        {:else}
            <button class="toolbar" on:click={() => { player.play(playhead); }} bind:this={playBtn} />
        {/if}
        <button class="toolbar" on:click={() => { player.pause(); playhead = 0; }} bind:this={stopBtn} />
    </div>
</div>

<style>
    .audio {
        border: var(--jp-border-width) solid var(--jp-cell-editor-border-color);
        border-radius: 0px;
        background: var(--jp-cell-editor-background);
        
        display: flex;
        height: 28px;
    }

    .audio > * {
        padding: 0px 10px;
    }

    .audio > *:not(:last-child) {
        border-right: var(--jp-border-width) solid var(--jp-cell-editor-border-color);
    }

    .audio > .meta {
        line-height: 28px;
    }

    .audio > .slider {
        padding: 0;
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
    export let component;

    import BufferSlider from "./BufferSlider.svelte";

    import { AudioSource } from "./rpc";
    import { AudioPlayer } from "./player";
    import { onMount, onDestroy, tick } from "svelte";

    let myself;

    const audioSource = new AudioSource(component);
    const player = new AudioPlayer(audioSource);

    let playhead = 0;
    let proposed = null;

    let sample_count = 0;
    let sample_rate = 0;
    let samples = 1;
    let loaded = 0;

    let seeking = false;
    let playing = false;

    $: percBuffered = samples / loaded;

    onMount(async () => {
        audioSource.open();
        audioSource.loadMetadata();
        audioSource.ondata = () => {
            sample_count = audioSource.samples;
            sample_rate = audioSource.sample_rate;
            samples = audioSource.samples;
        }

        player.ontick = (event) => {
            if (seeking) return;
            playing = event.playing;
            playhead = event.currentTime * audioSource.sample_rate;
            loaded = event.bufferSecond * audioSource.sample_rate;
        };
    });

    onDestroy(() => {
        audioSource.close();
        player.pause();
    });

    async function seek(event) {
        // Run as expected if we are not playing back.
        if (!playing) return;

        // Pause and restart at the desired position.
        seeking = true;
        player.pause();
        while (!player.playable) {
            await new Promise(rs => setTimeout(rs, 1));
        }
        seeking = false;
        player.play(event.detail.new);
    }

    $: displaySamples = proposed === null ? playhead : proposed;
    $: raw_seconds = Math.round(displaySamples / sample_rate);
    $: seconds = raw_seconds % 60;
    $: minutes = Math.floor(raw_seconds / 60) % 60;
    $: hours = Math.floor(raw_seconds / 3600);

    $: displayTimeMinutes = `${(minutes+"").padStart(2, "0")}:${(seconds+"").padStart(2, "0")}`;
    $: displayTime = (hours < 1) ? displayTimeMinutes : `${hours}:${displayTimeMinutes}`;

    let playBtn, pauseBtn, stopBtn;

    import { refreshIcon, runIcon, stopIcon } from "@jupyterlab/ui-components";

    $: if (!!stopBtn) refreshIcon.element({ container: stopBtn, width: '16px', height: '16px', marginLeft: '2px' });
    $: if (!!playBtn) runIcon.element({ container: playBtn, width: '16px', height: '16px', marginLeft: '2px' });
    $: if (!!pauseBtn) stopIcon.element({ container: pauseBtn, width: '16px', height: '16px', marginLeft: '2px' });
</script>

