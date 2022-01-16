<span bind:this={ target }>
</span>

<script>
    import * as Icons from "@jupyterlab/ui-components";

    export let icon = "jupyter";
    export let style = "width: 16px; height: 16px; margin-left: 2px;";

    let target;

    function updateIcon(target, iconName, style) {
        if (!target) return;

        const icon = Icons[iconName + "Icon"];
        if (!Icons[iconName + "Icon"]) return;

        target.innerHTML = "";
        const result = icon.element({ container: target });
        result.setAttribute("style", style);
    }

    $: updateIcon(target, icon, style);
</script>
