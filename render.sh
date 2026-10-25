#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p scenes renders
blender -b --python-exit-code 1 -t 5 --python scene.py -- --stage baseline --samples 64
blender -b --python-exit-code 1 -t 5 --python scene.py -- --stage improved --samples 64
blender -b --python-exit-code 1 -t 5 --python refine_scene.py -- --samples 96
blender -b --python-exit-code 1 -t 5 --python interior_scene.py -- --view left --samples 96
blender -b --python-exit-code 1 -t 5 --python interior_scene.py -- --view detail --samples 96
