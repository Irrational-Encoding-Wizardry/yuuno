import "./wrapper.css";
import "xterm/css/xterm.css";

import { define } from "./requirejs";
define("yuuno-platform", () => require("@yuuno/widgets"));

console.log("Yuuno for Jupyter Notebook has been enabled successfully.")
export * from "@yuuno/widgets";
