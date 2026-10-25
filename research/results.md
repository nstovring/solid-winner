# Experiment results

## Reproduction
Blender 4.3.2, Cycles CPU, five rendering threads, 1200 × 850, 64 samples, AgX, no denoising. Both stages use the same camera and light powers. A separate fixed city seed keeps the skyline identical despite different vegetation counts. Use `./render.sh` from the repository root.

## Observed comparison and validation
Both final Blender commands exited successfully and produced their PNGs and editable scene files. Both PNGs were opened and visually inspected. The improved render shows noticeably stronger warm reflections on paving, mottled surfaces, roof seams, paint loss on the tram and fuller plants. The overall silhouettes and camera remain the same. It still reads as a diorama rather than a photograph. The extra plants below the terrace expose an implementation weakness: they are separate potted objects instead of connected trailing vines, and should be replaced in the next geometry pass.

An initial attempt failed because the installed build lacks OpenImageDenoise; disabling the unsupported feature and using matching 64-sample renders resolved it. Python compilation and shell syntax checks also passed. No automated visual rating or fresh-task snapshot restoration was tested.

## Scope
The generator builds an elevated terrace, station storefront, open doorway, shelves, timber table and benches, laptop, stair flight, railings, teal funicular, track sleepers, practical lights, utility pipes, plants and a windowed skyline. No external assets or image textures are required. All geometry remains editable in the saved Blender files.

## Limitations against the reference
This is a simplified procedural diorama, not a photorealistic recreation. The reference has much denser architectural construction, hanging infrastructure, convincing interiors, glass reflections, detailed vegetation, directional wear, city haze, distant geography and rich wet-surface variation. The current tram has open window bays without glazing. The staircase is a schematic flight and the tower/skyline have simple block silhouettes. Noise textures do not substitute for detailed scanned materials. A further pass should prioritize structural detail, physically plausible glass and windows, spatially masked wetness/rain streaks, richer city geometry, atmospheric depth, and a closer camera composition.

## Workflow interpretation
The written plan makes the improvement pass inspectable and repeatable. This single experiment does not establish that a research/report step outperforms spending the same time on direct iteration. External documentation requests were blocked or unavailable; the report labels that limitation explicitly. A controlled follow-up could compare equal-time direct iteration and report-first branches with independent visual ratings.
