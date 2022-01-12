<div class="encode">
    <div>
        <Header component={ component } />
    </div>

    <div>
        <Terminal component={ component } />
    </div>
</div>

<style>
    .encode {
        border: var(--jp-border-width) solid var(--jp-cell-editor-border-color);
        border-radius: 0px;
        background: var(--jp-cell-editor-background);
        
        display: flex;
        flex-direction: column;
    }

    .encode > * {
        width: 100%;
    }
</style>

<script>
    export let component;

    import Header from './Header.svelte';
    import Terminal from "./Terminal.svelte";
</script>
