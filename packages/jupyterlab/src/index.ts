import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICodeMirror } from "@jupyterlab/codemirror";
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { IJupyterWidgetRegistry } from "@jupyter-widgets/base";

import * as Widgets from "@yuuno/widgets";

import { addPythonModeForExtension } from "./codemirror";


function registerIPythonWidgets(registry: IJupyterWidgetRegistry|null) {
    if (registry === null) return;

    registry.registerWidget({
        name: "yuuno-platform",
        version: "1.2.0",
        exports: Widgets
    });
    console.log('@yuuno/jupyterlab: Widgets registered.');
}


function registerCodeMirrorExtensions(codemirror: ICodeMirror) {
    addPythonModeForExtension(codemirror.CodeMirror, "vpy");
    console.log('@yuuno/jupyterlab: Registered vpy as Python extension.');
}


function registerSettingsRegistry(settingRegistry: ISettingRegistry|null) {
    if (settingRegistry === null) return;
    settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('@yuuno/jupyterlab settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error('Failed to load settings for @yuuno/jupyterlab.', reason);
        });
}

/**
 * Initialization data for the @yuuno/jupyterlab extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
    id: '@yuuno/jupyterlab:plugin',
    autoStart: true,
    requires: [ICodeMirror],
    optional: [IJupyterWidgetRegistry, ISettingRegistry],
    activate: (
          app: JupyterFrontEnd,
  
          codeMirror: ICodeMirror,
  
          widgets: IJupyterWidgetRegistry|null,
          settingRegistry: ISettingRegistry | null
    ) => {
        registerIPythonWidgets(widgets);
        registerCodeMirrorExtensions(codeMirror);
        registerSettingsRegistry(settingRegistry);
        console.log('JupyterLab extension @yuuno/jupyterlab is activated with app', app);
    }
};

export default plugin;
