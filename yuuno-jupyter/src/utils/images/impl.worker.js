import JIMP from 'jimp/es';

const dispatchers = {
    async resize({w, h, buffer}) {
        let img = await JIMP.read(buffer);
        const buf = (await img.resize(w, h, JIMP.RESIZE_NEAREST_NEIGHBOR).getBufferAsync(JIMP.MIME_PNG)).buffer;
        return [{
            resized: buf
        }, [buf]]
    }
}


self.onmessage = (event) => {
    const {id, type, payload} = event.data;
    dispatchers[type](payload).then(
        (response) => self.postMessage({id, type: "response", payload: response[0]}, response[1]),
        (error) => self.postMessage({id, type: "failure", payload: error})
    );
}