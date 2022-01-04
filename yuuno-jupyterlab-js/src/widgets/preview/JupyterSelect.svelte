<div class="jp-HTMLSelect jp-DefaultStyle jp-Notebook-toolbarCellTypeDropdown yuuno-fake">
    <select title={ title } bind:value={ value }>
        <slot></slot>
    </select>

    <span bind:this={iconTarget}></span>
</div>

<style>
    .yuuno-fake {
        display: flex;
    }
</style>


<script>
    export let title = "";
    export let value;
    import { caretDownEmptyIcon } from '@jupyterlab/ui-components';

    let iconTarget;
    $: caretDownEmptyIcon.element({
        container: iconTarget,
        width: '16px',
        height: '16px',
        marginLeft: '2px'
    });
</script>
