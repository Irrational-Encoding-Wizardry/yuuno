import type CodeMirror from "codemirror";


export function addPythonModeForExtension(codemirror: typeof CodeMirror, extension: string): void {
    const pythonMode = (<any>codemirror).findModeByExtension("py");
    if (pythonMode === undefined) throw new Error("Python Mode not supported for some reason?");
    pythonMode.ext!.push(extension);
}


