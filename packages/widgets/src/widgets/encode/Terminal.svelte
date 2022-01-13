<div bind:this={ target } class="terminal" />

<style>
    .terminal {
        width: 100%;
        min-height: 480px
    }
</style>

<script context="module">
    let self_id = 0;
</script>

<script>
    export let component;
    export let channel;

    const myOwnId = `terminal-${self_id}`;

    let target;
    let state = "attaching";

    import { onDestroy, onMount, tick } from "svelte";

    import { Terminal } from "xterm";
    import { FitAddon } from 'xterm-addon-fit';

    import { getRPCForModel } from "./rpc";

    const terminal = new Terminal();
    const fit = new FitAddon();
    terminal.loadAddon(fit);

    const rpc = getRPCForModel(channel);

    const cb = (msg) => {
        if (msg.type !== "write") return;
        if (state !== "ready") return;
        if (msg.target !== "broadcast") return;

        terminal.write(msg.data);
    };

    $: if (!!target) terminal.open(target);

    onMount(async () => {
        rpc.open();
        component.on("msg:custom", cb);
        terminal.write((await rpc.refresh({ source: myOwnId })).data);
        state = "ready";
    });

    onMount(async () => {
        // Let's do our best to enforce style calculations.
        await new Promise(rs => requestAnimationFrame(rs));
        await new Promise(rs => requestAnimationFrame(rs));

        // This is a trick.
        window.getComputedStyle(target).width;

        // Now fit the terminal size.
        fit.fit();
    });

    onDestroy(() => {
        component.off("msg:custom", cb);
        rpc.close();
    });
</script>
