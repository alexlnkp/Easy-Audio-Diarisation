#!/bin/bash

apt-get update

THEME="gradio/soft"

while [[ $# -gt 0 ]]; do
    case $1 in
        --iscolab)
            FLAGS+=" --iscolab"
            ;;
        --paperspace)
            FLAGS+=" --paperspace"
            ;;
        --not-autolaunch)
            FLAGS+=" --not-autolaunch"
            ;;
        --theme)
            shift
            FLAGS+=" --theme $1"
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

python gui.py $FLAGS

read -p "Press Enter to exit."