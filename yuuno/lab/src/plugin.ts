import {
    JupyterLabPlugin
} from "@jupyterlab/application";

const extension: JupyterLabPlugin<void> = {
    id: 'yuuno.lab',
    autoStart: true,

    activate: (app) => {
        console.log('Loading Yuuno Extension for Jupyter-Lab');
    }
};

export default extension;
