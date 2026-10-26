# LAST STOP bedroom: design to implementation

## Asset scope

`bedroom_funicular.py` builds the bedroom funicular as a fresh standalone Blender scene. It does not load any earlier station `.blend` file. The car is organized into **Shell, Roof, Glazing, Interior, Textiles, Props, Lights and Stage** groups, allowing the object, lighting and presentation to be inspected separately.

The starting envelope is approximately 2.4 m wide and 5.1 m long. The front cab is retained as a work area, the side entry remains clear, and the rear-left contains a 120 × 190 cm mattress. This implements the [LAST STOP design brief](../designs/funicular-bedroom.md) as an editable object study rather than modifying the station environment.

## Fittings and personal objects

`bedroom_props.py` exports `add_bedroom_props(materials)` and creates its fittings in the active scene. It has no scene-loading or rendering behavior at import time. `blender_shapes.py` supplies mesh, curve, lathe and text helpers.

The prop module builds:

- A fitted timber desktop following the front windscreen profile, with mounting brackets, retained lever, round instrument gauges and switches labeled ROOM and SIGN.
- A stool that tucks beneath the desktop, notebook, repaired audio player and clipped cable run.
- A shallow mid-left cabinet, coat hooks, fabric strap and folded cloth.
- A small bedside niche containing a paperback and enamel mug.
- A rear-right storage ledge, zines, cassette case and pencil cup.
- A front destination housing reading LAST STOP, with mounting brackets and a supply cable.

The right ledge occupies **X=.85 to 1.05 m**, leaving **.68 m** beside the mattress edge at X=.17 m. This matches the brief's 65–75 cm aisle target at that section. Handles, loose objects, the entry mechanism and final wall thickness still need inspection together in the assembled model.

The props use deliberate shapes—lathed vessels, curved handles, shaped desktop profiles and round gauges—rather than treating every object as a beveled cube.

## Textiles and lighting intent

The main generator supplies the mattress, patched quilt, folded wool throw, tied curtains, shell and lights. Quilt folds are generated as controlled procedural geometry; they are not the output of a cloth simulation. Their success must be assessed by silhouette, contact and apparent fabric weight in the rendered views.

Warm domestic lighting is intended to dominate the sleeping area, with restrained magenta and cyan accents. The neon should remain attached to identifiable fixtures and should not overwhelm fabric color or conceal the material work.

## Rendered views

1. **Hero:** an intact exterior view showing the vehicle silhouette, entry and warm interior through the windows.
2. **Entry:** a view through the open side door to evaluate the bed, circulation and front cab at different depths.
3. **Cutaway:** a clearly labeled roof-off layout view for checking the furniture fit and interior construction.

The cutaway is an inspection presentation; it should not be mistaken for the intact exterior object.

## Validation status

Python compilation and a Blender 4.3.2 smoke check passed for the prop module. The initial smoke check created 93 fitting objects and confirmed the LAST STOP text. The ledge was subsequently narrowed to the dimensions above and Python compilation was repeated.

The complete generator ran successfully in Blender 4.3.2. All three final 1440 × 1080 images were rendered at 96 Cycles samples and opened for visual inspection. Hero, entry and cutaway rendering took approximately 1:45, 2:45 and 2:01 respectively on the current machine. Denoising is disabled because this installed Blender build lacks OpenImageDenoise, so visible grain remains.

The saved `scenes/funicular-bedroom.blend` was independently reopened. It retains all three cameras, the intact roof as its default state, the hero camera, and `LAST_STOP_ASSET_ROOT` as the parent of the model parts and its practical lighting. The studio remains separate. Mattress dimensions are approximately 1.19 × 1.90 m on a nominal 1.20 m bed platform. Measured aisle clearance is 0.685 m beside the mattress and 0.665 m beside the quilt's outermost vertex. These values describe that cross-section, not a full collision or accessibility certification.

The first draft exposed inward-facing box polygons in the shared shape helper, making glass appear too dark. `blender_shapes.py` now creates outward-facing box polygons; normals were checked on the actual saved side glass. Existing station render files were retained. A local 20-sample roof-off check with `--neon-off` was also inspected: warm fixtures still illuminate the bed and wood without the magenta/cyan accent lights.

Python compilation and Git whitespace checks passed. Final renders visibly show the warm bedroom through the glazing and doorway; the cutaway makes the furniture fit clear. This is an editable stylized asset, not a fabrication-ready vehicle conversion. The entry camera intentionally includes the door frame, which obscures part of the rear bedding. Some trim and weathering remain regular, and the textile shapes are controlled procedural approximations rather than simulated fabric. These are useful targets for a subsequent focused detail pass.

The asset uses Blender Python procedural modeling. No external AI mesh generation, downloaded assets or add-ons are involved in these fittings.

## Reproduce

Run from the repository root:

```sh
blender -b --python-exit-code 1 -t 5 --python bedroom_funicular.py -- --view all --samples 96
```

The generator starts from a fresh scene and does not depend on the station files. It writes `scenes/funicular-bedroom.blend` plus `renders/bedroom-hero.png`, `renders/bedroom-entry.png` and `renders/bedroom-cutaway.png`. A quick `--samples 24 --scale 50` draft overwrites the selected PNGs without saving the full-size Blender file; rerun the full command to restore final images. `--neon-off` creates separate `-warm` images for lighting evaluation.
