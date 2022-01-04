<span>{ running_time }</span>

<script>
    export let end_time;
    export let start_time;

    export let terminated;

    import { onDestroy } from 'svelte';

    let clock = new Date().valueOf();
    let interval = setInterval(() => {
        clock = new Date().valueOf();
    }, 1000);
    onDestroy(() => {
        clearInterval(interval);
    });

    $: current_time = terminated ? end_time : Math.round(clock/1000);
    $: dTime = current_time - start_time;

    $: seconds = dTime % 60;
    $: minutes = Math.round(dTime / 60) % 60;
    $: hours = Math.round(dTime / 3600) % 24;
    $: days = Math.round(dTime / 86400);

    $: intra_day = `${(minutes+"").padStart(2, "0")}:${(seconds+"").padStart(2, "0")}`
    $: running_time = days > 0 ? `${days+""}:${(hours+"").padStart(2, "0")}:${intra_day}` : `${hours+""}:${intra_day}`;
</script>
