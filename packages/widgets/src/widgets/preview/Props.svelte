<button class="toolbar" on:mouseenter={() => showTooltip=true} on:mouseleave={() => showTooltip = false} use:popperRef>
    <JupyterIcon icon="list" />
</button>

{#if showTooltip}
  <div class="tooltip" use:popperContent={popperOptions}>
    <table>
      <thead>
        <tr>
          <th>Property</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody>
        {#each [...Object.keys(props)].sort() as key}
        <tr>
          <td>{ key }</td>
          <td>
            {#each props[key] as value}
              <div>{ value }</div>
            {/each}
          </td>
        </tr>
        {/each}
      </tbody>
    </table>
    <div class="arrow" data-popper-arrow />
  </div>
{/if}

<script>
    import JupyterIcon from "../../components/JupyterIcon.svelte";

    import { createPopperActions } from 'svelte-popperjs';
    const [popperRef, popperContent] = createPopperActions();
    const popperOptions = {
        modifiers: [
            { name: 'offset', options: { offset: [2, 5] } }
        ],
    };
  
    let showTooltip = false;

    export let props = {};
</script>

<style>
    .tooltip {
        z-index: 10;
        background-color: rgba(0, 0, 0, 0.95);
        border-radius: 2px;
        padding: 10px;
    }

    table th {
        border-bottom: 1px solid white;
    }

    table td:first-child, table th:first-child {
        text-align: left;
    }

    table td:last-child, table th:last-child {
        text-align: left;
    }

    table {
        white-space: pre-wrap;
        font-family: monospace;
    }

    .arrow {
        top: -10px;
        width: 0;
        height: 0;
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-bottom: 10px solid black;
    }

    .toolbar {
        border: 0;
        background: transparent;
        margin: 0;
        padding: 0;
        line-height: 35px;
    }
</style>
