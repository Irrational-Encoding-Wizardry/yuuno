#!/usr/bin/env bash

runBuild() {
    pushd $1
    yarn run build
    popd
}

lerna bootstrap

pushd packages
runBuild widgets
runBuild jupyterlab
runBuild notebook
popd

jupyter labextension develop --overwrite .
