#!/usr/bin/env bash

base_path="$(pwd)"

function genexample() {
    old_pwd="$(pwd)"
    cd "${base_path}/mockdown"

    python mockdown.py ../examples/complete.mock.yaml ~/complete.html

    cd "$old_pwd"
}

function run() {
    old_pwd="$(pwd)"
    cd "${base_path}/mockdown"

    python mockdown.py "$@"

    cd "$old_pwd"
}

function test() {
    old_pwd="$(pwd)"
    cd "${base_path}"

    python -m unittest mockdown/mockdowntests.py

    cd "$old_pwd"
}

function install() {
    old_pwd="$(pwd)"
    cd "${base_path}"

    sudo pip install .

    cd "$old_pwd"
}