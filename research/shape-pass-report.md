# Shape and composition pass

## Evaluation

The first improvement pass changes surfaces, edge highlights and vegetation density, but the scene still reads as a diorama. Most recognizable objects share the same rectangular construction: the tram roof, vehicle front, jars, lanterns and skyline are boxes. Generic bump cannot repair a silhouette. Several plants below the terrace are unsupported pots, which also breaks physical plausibility.

The next pass should spend detail on shapes that communicate a specific object or construction method. Buildings can retain flat planes; the vehicle roof, foliage, vessels, cables and trim need purposeful curves.

## Priorities

1. **Tram silhouette.** Replace the slab roof with a shallow barrel roof built from an extruded arch profile. Add rounded body corners, curved window-frame corners, thin glazing and cylindrical headlights. These cues help the tram read as a manufactured vehicle instead of a room on rails.
2. **Connected organic growth.** Replace faceted plant blobs and floating pots with curved stems and trailing vines attached to pots or slab edges. Instance pointed leaf meshes with varied orientation, scale and clustering. Preserve clear support for every planter.
3. **Architectural silhouette variety.** Break up the monolithic support tower and repeated skyline boxes with setbacks, roof equipment, cylindrical tanks, balconies, connecting bridges and support beams. A few parameterized building families are more useful than arbitrary deformation of every building.
4. **Recognizable rounded props.** Model jars, bowls, mugs, lantern housings and headlights with cylinders or lathed profiles, then add curved handles and suitable trim. The different shapes communicate use and human scale.
5. **Construction and framing.** Add stair sidewalls or stringers, landing supports, balcony ribs, and bends/junctions in pipes and cables. Tighten framing toward the terrace and tram, and reduce distant-city contrast so the improved geometry occupies more useful pixels.

## What “generative” means here

Blender procedural modeling is a good fit: Bézier curves, profile extrusion, bevels, instancing and Geometry Nodes can generate editable variation with explicit constraints. Geometry Nodes is especially suitable for scattering leaves along stems or producing families of buildings. The same geometry can be constructed deterministically through Blender's Python API.

This pass uses Python-built curves, lathed profiles, shaped meshes and deterministic instancing. It does not invoke external AI mesh generation, install AI add-ons, or claim that writing Python geometry is an AI mesh service. External AI-generated assets could later contribute individual background props, but their topology, scale, material consistency and placement would still need review. They would not automatically correct composition or structural logic.

## Implementation

`refine_scene.py` loads the existing `scenes/improved.blend` and writes a third version to `scenes/refined.blend` and `renders/refined.png`. The original baseline and first improved scene/render remain available. The implementation also replaces the emissive doorway card with a real opening, a shallow furnished room and a warm light. The third pass changes camera and lighting as well as geometry, so this is an art-direction iteration rather than a controlled material-only comparison.

Both draft and final renders were inspected for tram silhouette, plant attachment, prop readability, depth and framing. The final command completed successfully. See [shape-pass-results.md](shape-pass-results.md) for observed gains and remaining limitations; this does not establish photorealism.
