#!/usr/bin/env bash

base_path="$(pwd)"

function genexample() {
    pushd . &> /dev/null
    cd "${base_path}/mockdown"

    python mockdown.py ../examples/complete.mock.yaml ~/complete.html

    popd
}

function run() {
    pushd . &> /dev/null
    cd "${base_path}/mockdown"

    python mockdown.py "$@"

    popd
}

function test() {
    pushd . &> /dev/null
    cd "${base_path}/mockdown"

    python -m unittest mockdowntests.py

    popd
}