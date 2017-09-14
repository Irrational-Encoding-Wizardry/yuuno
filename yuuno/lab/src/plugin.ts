// Yuuno - IPython + VapourSynth
// Copyright (C) 2017 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
import {
    JupyterLabPlugin,
    JupyterLab,
} from "@jupyterlab/application";
const extension: JupyterLabPlugin<void> = {
    id: 'yuuno.lab',
    autoStart: true,

    activate: (app: JupyterLab) => {
        console.log('Loading Yuuno Extension for Jupyter-Lab');
        // TODO: Stub
    },
};

export default extension;
