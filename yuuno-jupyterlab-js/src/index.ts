import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICodeMirror } from "@jupyterlab/codemirror";
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { IJupyterWidgetRegistry } from "@jupyter-widgets/base";

import { PreviewWindowWidget } from "./widgets/preview/index";
import { EncodeWindowWidget } from "./widgets/encode/index";
import { AudioPlaybackWidget } from "./widgets/audio/index";

import { addPythonModeForExtension } from "./codemirror";

/**
 * Initialization data for the @yuuno/jupyterlab extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@yuuno/jupyterlab:plugin',
  autoStart: true,
  requires: [IJupyterWidgetRegistry, ICodeMirror],
  optional: [ISettingRegistry],
  activate: (app: JupyterFrontEnd, widgets: IJupyterWidgetRegistry, codeMirror: ICodeMirror, settingRegistry: ISettingRegistry | null) => {
    widgets.registerWidget({
        name: "@yuuno/jupyter",
        version: "1.2.0",
        exports: {
            PreviewWindowWidget,
            EncodeWindowWidget,
            AudioPlaybackWidget
        }
    });
    console.log('@yuuno/jupyterlab: Widgets registered.');

    addPythonModeForExtension(codeMirror.CodeMirror, "vpy");
    console.log('@yuuno/jupyterlab: Registered vpy as Python extension.');

    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('@yuuno/jupyterlab settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error('Failed to load settings for @yuuno/jupyterlab.', reason);
        });
    }

    console.log('JupyterLab extension @yuuno/jupyterlab is activated with app', app);
  }
};

export default plugin;
