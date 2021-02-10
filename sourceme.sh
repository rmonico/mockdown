#!/usr/bin/env bash

base_path="$(pwd)"

function genexample() {
    pushd "${base_path}/mockdown" &> /dev/null

    python mockdown.py ../examples/complete.mock.yaml ~/complete.html

    popd
}

function run() {
    pushd "${base_path}/mockdown" &> /dev/null

    python mockdown.py "$@"

    popd
}

function test() {
    pushd "${base_path}" &> /dev/null

    python -m unittest mockdown/mockdowntests.py

    popd
}