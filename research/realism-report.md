# Summit station: realism improvement plan

## Experiment
Reconstruct the supplied image as an editable Blender environment, render a baseline, then implement an explicit improvement pass. Preserve camera, architecture, resolution, lighting powers and color management for comparison. This is an approximation from one image, not recovered geometry or an exact reproduction. No image generation is used for the renders.

## Reference observations
The reference combines a close, elevated terrace with a huge blue-hour city. Its important cues are warm occupied interiors, a weathered teal funicular, wet paving, narrow metal railings, plants growing around neglected infrastructure, and layered distant architecture. The warm/cool contrast and believable wear contribute more than adding arbitrary small props.

## Prioritized recommendations
1. **Break perfect edges.** Add small bevels and weighted normals to hard surfaces, allowing highlights to describe thickness. Keep bevel width below the thickness of the object.
2. **Replace uniform materials.** Vary base color with procedural noise and add restrained bump. Concrete should look different from painted steel and wood. A first procedural pass will still lack directional rain streaks, grain, and physically localized corrosion.
3. **Wet paving.** Lower roughness and retain dark diffuse coloration to catch warm practical lights. A stronger future implementation should mask puddles and damp patches separately instead of making the whole terrace equally wet.
4. **Aging and construction detail.** Add paint loss to the tram, roof seams, and terrace debris. Localize subsequent wear near seams, drainage paths, and frequently touched edges.
5. **Organic variation.** Increase plant branching and add growth along slab edges. Avoid equally spaced identical plants.
6. **Depth and occupancy.** Retain city window variation and warm station/tram lighting. Atmospheric scattering would improve distance cues, but must be evaluated separately because it also changes exposure and contrast.

## Technical basis and research limitations
These recommendations use Blender's Principled BSDF, Noise Texture, Bump, Bevel, Weighted Normal, Cycles and AgX. Official manual pages attempted during this run:
- https://docs.blender.org/manual/en/4.3/render/shader_nodes/shader/principled.html
- https://docs.blender.org/manual/en/4.3/render/lights/light_object.html

Both requests returned HTTP 403. Attempts to retrieve a GitHub mirror returned 404. Therefore this is an analysis and implementation plan based on known rendering principles, not a claim of completed external literature research. Runtime validation uses the installed Blender 4.3.2 API.

## Comparison criteria
Inspect edge highlights, floor reflections, material variation, foliage density, silhouettes and overall readability. Report what actually changed and remaining limitations; do not equate added detail with achieved photorealism. Both renders use 64 samples without denoising. The installed Blender build lacks OpenImageDenoise support; an initial render failed on that capability, so the generator explicitly disables it. Both versions use the same rendering settings.
