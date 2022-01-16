<div class="header">
    <div class="top-bg">
        <Progress min={0} max={ $length } value={ $current } />
    </div>
    <div class="top">
        <div>{ $current } / { $length }</div>
        <div>
            <Clock start_time={ $start_time } end_time={ $end_time } terminated={ $terminated } />
        </div>
        <div class="spacer">{ $commandline }</div>
        {#if $terminated}
            <div>Terminated</div>
        {:else}
            <div>
                {#if !$_w32}
                    <button class="toolbar" on:click={() => { rpc.interrupt(); }}>
                        <JupyterIcon icon="close" />
                    </button>
                {/if}
                <button class="toolbar" on:click={() => { rpc.kill(); }}>
                    <JupyterIcon icon="stop" />
                </button>
            </div>
        {/if}
    </div>
</div>

<style>
    .header {
        width: 100%;
    }

    .top-bg {
        width: 100%;
        top: 0;
        left: 0;
    }

    .top {
        display: flex;
        line-height: 27px;
        height: 27px;
    }

    .top > * {
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
    export let component;
    export let channel;

    import JupyterIcon from "../../components/JupyterIcon.svelte";

    import Progress from "./Progress.svelte";
    import Clock from "./Clock.svelte";
    
    import { onMount, onDestroy } from "svelte";

    import { closeIcon, stopIcon } from "@jupyterlab/ui-components";

    import { model_attribute } from "../../utils"; 

    const commandline = model_attribute(component, "commandline");
    const current = model_attribute(component, "current");
    const length = model_attribute(component, "length");

    const terminated = model_attribute(component, "terminated");
    const start_time = model_attribute(component, "start_time");
    const end_time = model_attribute(component, "end_time");

    const _w32 = model_attribute(component, "_w32");

    import { getRPCForModel } from "./rpc";

    const rpc = getRPCForModel(channel);
    onMount(() => rpc.open());
</script>

