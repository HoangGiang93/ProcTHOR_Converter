#!/bin/bash

if [ ! -d "ai2thor" ]; then
    git clone git@github.com:allenai/ai2thor.git
fi

python get_meshes.py

python3.11 extract_objects.py