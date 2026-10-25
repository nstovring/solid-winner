# Shape-pass results

This is the third scene, after the original baseline and material pass. The original two renders and Blender files are preserved.

## What changed

- The tram has a shallow barrel-vault roof, curved roof seams/gutters, more rounded body edges, framed glazing, wipers, round headlights, wheels and a bent bumper.
- Plants use shared pointed leaf meshes on curved stems. Trailing vines are attached to the slab; unsupported hanging pots were removed. Supported pots use hollow lathed profiles.
- The shop has a curved canvas awning with a scalloped valance, round jars, and a recessed doorway instead of an emissive card. A small room behind it contains a bed, rounded mattress/pillow, blanket and warm light.
- The table has a hollow mug with a curved handle, coffee, a bowl and fruit. A cylindrical rooftop water tank and curved pipework add more varied silhouettes.
- Stairs have stringers, guard posts and a top landing. The tower gains floor belts, pilasters, inset windows and braces under the projecting slab.
- The city uses setbacks, balcony families, roof equipment, side windows and narrow connecting bridges. Fewer windows are lit, and a volume behind the station adds distance haze.
- The camera moves closer; the scene uses a darker blue fill with stronger local warm lighting. These choices are part of this iteration, not a controlled geometry-only comparison.

## Generative tools

All geometry is made in Blender using deterministic Python, shaped mesh profiles, Bézier curves, lathing and shared leaf meshes. No image generation, external AI mesh service, downloaded assets or Geometry Nodes add-on is involved. Geometry Nodes would be a suitable next step for exposing foliage/building parameters interactively; it is not necessary to get these shape improvements.

## Evaluation

Both the draft and final 1440 × 960 render were opened and visually inspected. The final command exited successfully at 96 samples and completed in approximately four minutes on this machine. The saved Blender file was independently reopened and confirmed to contain 1,252 objects, including 207 curves, 480 leaf instances and 20 attached vines; no old unsupported pots remained. Python compilation, shell syntax and Git whitespace checks passed. The arched tram roof, circular lights, awning, rounded vessels and more delicate plants are clear departures from the earlier box-based shapes. The terrace is more prominent in the composition. Structural detail makes the lower tower feel like a building rather than an undecorated plinth.

This remains a stylized reconstruction. Remaining gaps include overly rounded front window trim, sparse interiors, repeated city floor patterns, idealized concrete edges and broadly uniform wetness. The new furnished room is largely hidden by the door and camera angle, so the visible interior depth remains limited. The Boolean opening was applied successfully, although Blender emitted an informational modifier-order notice; it did not fail the render. Directional rain marks, puddle masks, more varied architecture and richer interior furnishings would be more useful next than indiscriminately adding subdivision or AI-generated props. The un-denoised CPU render also retains visible grain.

## Reproduction

Requires `scenes/improved.blend` from the previous pass. From the repository root:

```sh
blender -b --python-exit-code 1 -t 5 --python refine_scene.py -- --samples 96
```

Outputs: `scenes/refined.blend`, `renders/refined.png`. A quick draft uses `--samples 24 --scale 60` and overwrites those same two refined files. Run the full command afterwards to restore full-size outputs. The final rendering target is 1440 × 960, Cycles CPU, 96 samples, AgX, no denoising because this installed Blender build lacks OpenImageDenoise.
