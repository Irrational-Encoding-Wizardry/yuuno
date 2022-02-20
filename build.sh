#!/usr/bin/env bash

runBuild() {
    pushd $1
    if [ -d lib ]; then
      rm -rf lib
    fi
    if [ -f tsconfig.tsbuildinfo ]; then
      rm tsconfig.tsbuildinfo
    fi
    yarn run build
    popd
}

lerna bootstrap

pushd packages
runBuild widgets
runBuild jupyterlab
runBuild notebook
popd

if [ "$1" == "dev" ]; then
  jupyter labextension develop --overwrite .
  jupyter nbextension install yuuno --sys-prefix --py --symlink
  jupyter nbextension enable yuuno --sys-prefix --py
fi
