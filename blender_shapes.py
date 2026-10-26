"""Small Blender modeling helpers with no scene changes at import time.

Shapes keep their origin at the supplied center, so callers can rotate or parent
returned objects without moving their geometry around the world origin.
"""

import math

import bpy
from mathutils import Vector


def _mesh_object(name, vertices, faces, mat, center=(0, 0, 0), smooth=False):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = center
    obj.data.materials.append(mat)
    if smooth:
        for polygon in mesh.polygons:
            polygon.use_smooth = True
    return obj


def material(name, color, rough=.5, metal=0, emission=0):
    """Create a Principled material from an RGB color."""
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = rough
    shader.inputs['Metallic'].default_value = metal
    if emission:
        shader.inputs['Emission Color'].default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = emission
    return mat


def box(name, center, size, mat, edge=0):
    """Create a box directly from mesh data, optionally beveling its edges."""
    vertices = [
        (x * size[0] / 2, y * size[1] / 2, z * size[2] / 2)
        for x, y, z in [
            (-1, -1, -1), (-1, -1, 1), (-1, 1, -1), (-1, 1, 1),
            (1, -1, -1), (1, -1, 1), (1, 1, -1), (1, 1, 1),
        ]
    ]
    faces = [
        (0, 4, 6, 2), (1, 3, 7, 5), (0, 1, 5, 4),
        (2, 6, 7, 3), (0, 2, 3, 1), (4, 5, 7, 6),
    ]
    # Outward winding matters for dielectric interfaces such as window glass.
    faces = [tuple(reversed(face)) for face in faces]
    obj = _mesh_object(name, vertices, faces, mat, center)
    if edge:
        bevel = obj.modifiers.new('Rounded manufactured edge', 'BEVEL')
        bevel.width = edge
        bevel.segments = 3
        obj.modifiers.new('Weighted surface normals', 'WEIGHTED_NORMAL')
    return obj


def curve(name, points, radius, mat, cyclic=False):
    """Create a beveled Bézier curve through world-space points."""
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 10
    data.bevel_depth = radius
    data.bevel_resolution = 3
    spline = data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for bezier, point in zip(spline.bezier_points, points):
        bezier.co = point
        bezier.handle_left_type = 'AUTO'
        bezier.handle_right_type = 'AUTO'
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def lathe(name, center, profile, mat, segments=32):
    """Revolve (radius, height) profile points around a local Z axis."""
    vertices = [
        (radius * math.cos(i * math.tau / segments),
         radius * math.sin(i * math.tau / segments), height)
        for radius, height in profile
        for i in range(segments)
    ]
    faces = [
        (j * segments + i, j * segments + (i + 1) % segments,
         (j + 1) * segments + (i + 1) % segments, (j + 1) * segments + i)
        for j in range(len(profile) - 1)
        for i in range(segments)
    ]
    return _mesh_object(name, vertices, faces, mat, center, smooth=True)


def text(body, location, size, mat):
    """Create text facing toward -Y, retaining any newlines in body."""
    data = bpy.data.curves.new(body, 'FONT')
    data.body = body
    data.size = size
    data.extrude = .001
    obj = bpy.data.objects.new(body, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.pi / 2, 0, 0)
    obj.data.materials.append(mat)
    return obj


def area_light(name, location, power, color, size, target):
    """Create a disk area light oriented toward a world-space target."""
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.color = color
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()
    return obj
