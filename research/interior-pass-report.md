# Station interior and viewpoint pass

## Problem

The previous station was primarily a thin front wall. Its narrow doorway room was largely hidden by the door and camera angle, and shelves placed directly across the shop opening suppressed the view behind them. Surface detail and rounded props could not establish building depth.

This pass replaces that arrangement with an enclosed station volume and connected occupied spaces. It also tests lower exterior camera views. Geometry, lighting and camera all change, so this is an art-direction iteration rather than a controlled interior-only benchmark.

## Built layout

The station extends approximately five metres behind the front face, from y≈3.25 to y≈8.3, with a footprint about eight metres wide. A continuous roof, ceiling, ceiling joists, tiled floor, side returns and rear walls enclose the spaces; the exterior views retain the roof rather than using a cutaway.

- The café occupies the left side. A shallow service counter sits just inside the front opening; a separate backbar and espresso machine sit several metres behind it. Shelves, jars and a menu occupy the rear wall. A small round tea table and stools sit between these layers, leaving space around them.
- The right-side waiting area has an unobstructed entrance, a bench along the side wall, a timetable and a deeper passage toward an actual rear opening. A small rear landing suggests the connection to the platform.
- The entrance door is parented to a hinge and swung outward to clear the sightline, replacing the former panel across the opening.
- The left return includes a long, glazed window with thick reveals and mullions. Its purpose is to show the building's side depth and provide a second view into the café.
- Pendant lamps, exposed joists and a suspended fern provide overlapping near and far objects. Separate warm pools illuminate the front counter, backbar and waiting area; cooler fill comes from the rear passage.

The earlier terrace, funicular, foliage and city remain part of the setting. The awning is shortened to a roughly 0.4-metre projection to expose the rear shelves without raising it into the station sign, and the roof tank moves onto the new full roof.

## Camera reasoning

The first lower-camera drafts showed a clearer entrance and a visible waiting bench, but the main view was still close to frontal. The subsequent camera candidates move farther left to expose the return wall and side window. A closer companion view focuses on the café and passage. The tradeoff is that a stronger left angle can hide part of the tram's rear behind the station; preserving its recognizable front is sufficient for this pass's interior goal.

Three draft camera candidates were inspected for occlusion, then the main left-hand view and a more frontal close-up were rendered at full size and visually checked. Both commands completed successfully. See [interior-pass-results.md](interior-pass-results.md) for observed depth, limitations and validation evidence.

## Modeling and rendering limits

The station is modeled with Blender mesh geometry, lathed vessel profiles, curves and shared leaf meshes. It uses the local `blender_shapes.py` helpers and loads `scenes/refined.blend`. No external AI mesh generation, downloaded assets or add-ons are required. Objects remain editable in the saved Blender scenes.

The clear side window uses a Principled transmission material with a thin solid pane and IOR 1.45. Interior illumination uses emissive lamp diffusers plus area lights. These are practical scene approximations, not a calibrated architectural daylight simulation. The rear platform is a short landing rather than a fully engineered transit connection; circulation and furnishings communicate the scene's function without establishing a construction-ready floor plan.

Rendering uses Blender 4.3.2 Cycles CPU and AgX. Denoising remains disabled because the installed Blender build lacks OpenImageDenoise. The final target is 1440 × 960 at 96 samples. Un-denoised grain, simplified materials, sparse furnishings and repeated distant architecture remain expected limitations.

## Reproduce

Run from the repository root with the prior `scenes/refined.blend` available:

```sh
blender -b --python-exit-code 1 -t 5 --python interior_scene.py -- --view left --samples 96
blender -b --python-exit-code 1 -t 5 --python interior_scene.py -- --view detail --samples 96
```

The main view writes `renders/interior.png` and `scenes/interior.blend`. The close view writes `renders/interior-detail.png` and `scenes/interior-detail.blend`. Full-resolution single-view runs save compressed editable Blender files.

For camera evaluation, use:

```sh
blender -b --python-exit-code 1 -t 5 --python interior_scene.py -- --view all --samples 20 --scale 50
```

This generates main, front and detail draft PNGs, overwriting the corresponding images but not saving full-size scene files. Run the two full-resolution commands afterwards to restore the intended main and detail outputs. Preserve Blender's exit status and inspect the actual rendered images; a saved file alone does not establish that the interior is visible.
