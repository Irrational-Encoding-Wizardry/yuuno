import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { IJupyterWidgetRegistry } from "@jupyter-widgets/base";

import { PreviewWindowWidget } from "./widgets/preview/index";
import { EncodeWindowWidget } from "./widgets/encode/index";
import { AudioPlaybackWidget } from "./widgets/audio/index";

/**
 * Initialization data for the @yuuno/jupyterlab extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@yuuno/jupyterlab:plugin',
  autoStart: true,
  requires: [IJupyterWidgetRegistry],
  optional: [ISettingRegistry],
  activate: (app: JupyterFrontEnd, widgets: IJupyterWidgetRegistry, settingRegistry: ISettingRegistry | null) => {
    console.log('JupyterLab extension @yuuno/jupyterlab is activated!');

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

    // requestAPI<any>('get_example')
    //   .then(data => {
    //     console.log(data);
    //   })
    //   .catch(reason => {
    //     console.error(
    //       `The yuuno_jupyterlab server extension appears to be missing.\n${reason}`
    //     );
    //   });
  }
};

export default plugin;
