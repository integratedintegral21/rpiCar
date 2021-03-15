#!/bin/bash

onKeyboardInterrupt(){
    echo "Giving up"
    exit -1
}

trap onKeyboardInterrupt SIGINT
raspivid -o $1 -t 0 -n -w $2 -h $3 -fps 15 -vf -hf
