#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p scenes renders
blender -b --python-exit-code 1 -t 5 --python scene.py -- --stage baseline --samples 64
blender -b --python-exit-code 1 -t 5 --python scene.py -- --stage improved --samples 64
