import "./wrapper.css";
import "xterm/css/xterm.css";

// Entry point for the notebook bundle containing custom model definitions.
//
// Setup notebook base URL
//
// Some static assets may be required by the custom widget javascript. The base
// url for the notebook is not known at build time and is therefore computed
// dynamically.
// eslint-disable-next-line @typescript-eslint/no-non-null-assertion
(window as any).__webpack_public_path__ =
  document.querySelector('body')!.getAttribute('data-base-url') +
  'nbextensions/yuuno-platform';


import { define } from "./requirejs";
define("yuuno-platform", () => require("@yuuno/widgets"));

console.log("Yuuno for Jupyter Notebook has been enabled successfully.")
export * from "@yuuno/widgets";
