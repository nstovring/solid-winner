# Summit station workflow experiment

A procedural Blender reconstruction inspired by the supplied elevated funicular-station image. This repository tests **baseline → written realism report → implementation → comparison**.

## Latest comparison: shape and composition pass

The new pass uses curved profiles, lathed vessels, shared leaf meshes and Bézier vines. It also changes the framing, city, atmosphere and lighting; this is an art-direction iteration rather than a controlled geometry-only benchmark.

| Previous improved scene | New shape pass |
| --- | --- |
| ![Previous improved render](renders/improved.png) | ![New shape pass](renders/refined.png) |

[Full-size previous render](renders/improved.png) · [Full-size new render](renders/refined.png) · [Original baseline](renders/baseline.png)

The new editable scene is [scenes/refined.blend](scenes/refined.blend). Read [the shape evaluation](research/shape-pass-report.md) for the reasoning and [the pass results](research/shape-pass-results.md) for observed changes and remaining gaps.

## Reproduce

Requires Blender 4.3.2; no add-ons, downloads, credentials, or Python packages are needed.

```sh
cd /workspace/solid-winner
mkdir -p scenes renders
blender -b --python-exit-code 1 -t 5 --python scene.py -- --stage baseline --samples 64
blender -b --python-exit-code 1 -t 5 --python scene.py -- --stage improved --samples 64
blender -b --python-exit-code 1 -t 5 --python refine_scene.py -- --samples 96
```

Outputs: editable `scenes/baseline.blend`, `scenes/improved.blend` and corresponding PNGs under `renders/`. The third command loads `scenes/improved.blend` and creates `scenes/refined.blend` plus `renders/refined.png` at 1440 × 960. Use `--samples 24 --scale 60` on `refine_scene.py` for a quick draft; this overwrites only the refined outputs. Open any scene in Blender to inspect objects, materials and camera. Render output locations are resolved relative to the scene file. Run generation from this repository root.

Read [the improvement report](research/realism-report.md) and [results](research/results.md). The renders use actual geometry and Cycles, not image generation. This is a stylized approximation; the original's detail and photorealism are not guaranteed.

`./render.sh` reproduces all three stages. To rerender only the latest pass, run the `refine_scene.py` command with the existing improved scene. No add-on or external AI mesh service is required; the procedural geometry is constructed through the Blender Python API.
