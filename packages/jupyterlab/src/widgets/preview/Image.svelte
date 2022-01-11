<img src={ currentImageURL } alt="Frame: { frame }" width="{ size[0] }px" height="{ size[1] }px" class="{ extraZoomClass }" />

<style>
    img.zoomed {
        image-rendering: pixelated;
    }
</style>

<script>
    export let rpc;
    export let frame;
    export let type = "clip";
    export let zoom = 1;

    import { onDestroy } from 'svelte';

    let currentSize = [1, 1];
    let currentImageURL = null;
    let nextRequestFrame = null;
    let currentPromise = null;

    let pixelRatio = window.devicePixelRatio;
    let pixelRatioInterval = setInterval(1000, () => {
        pixelRatio = window.devicePixelRatio;
    });

    $: updateByFrameNo(frame);
    $: zoomFactor = zoom / pixelRatio;
    $: size = scaleSize(currentSize, zoomFactor);

    $: extraZoomClass = zoom != 1 ? "zoomed" : "";

    function scaleSize(sz, factor) {
        return [
            Math.max(1, Math.floor(sz[0] * factor)),
            Math.max(1, Math.floor(sz[1] * factor)),
        ]
    }

    function updateByFrameNo() {
        nextRequestFrame = frame;
        requestNext();
    }

    function requestNext() {
        if (currentPromise !== null) return;
        const currentFrame = nextRequestFrame;
        currentPromise = rpc.frame({ frame, image: type });
        currentPromise.then(() => {
            currentPromise = null;
            if (nextRequestFrame === currentFrame) return;
            requestNext();
        });
        currentPromise.then(({ size, buffers }) => {
            destroyExistingBlob();
            currentImageURL = URL.createObjectURL(new Blob([buffers[0]], { type: "application/json" }));
            currentSize = size;
        });
        currentPromise.catch(console.error);
    }

    function destroyExistingBlob() {
        if (currentImageURL !== null) {
            URL.revokeObjectURL(currentImageURL);
            currentImageURL = null;
        }
    }

    onDestroy(() => {
        destroyExistingBlob();
        clearInterval(pixelRatioInterval);
    });

</script>
