#! /bin/bash


load_env() {
    source ~/.bashrc
    cd ..
    venvinit
    cd interface
}

start_script() {
    python interface.py
}


load_env
start_script
