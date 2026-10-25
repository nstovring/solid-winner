"""A third art-direction pass; keeps the earlier two stages available for comparison."""
import argparse
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--samples', type=int, default=96)
parser.add_argument('--scale', type=int, default=100)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ROOT = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'scenes/improved.blend'))
random.seed(71)
scene = bpy.context.scene


def remove_prefix(*prefixes):
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)


def mesh_object(name, vertices, faces, material, smooth=False):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    if smooth:
        for poly in mesh.polygons:
            poly.use_smooth = True
    return obj


def material(name, color, rough=.5, metal=0, emission=0):
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


con = bpy.data.materials['Stained concrete']
wood = bpy.data.materials['Aged timber']
teal = bpy.data.materials['Oxidized teal paint']
iron = bpy.data.materials['Old steel']
cream = bpy.data.materials['Ivory enamel']
soil = bpy.data.materials['Terracotta']
leaf_mats = [material('Leaf variation %d' % i, c, .46) for i, c in enumerate([
    (.07, .15, .038), (.11, .22, .055), (.16, .26, .07), (.045, .095, .025)])]
ceramic = material('Glazed moss ceramic', (.11, .23, .20), .19)
coffee = material('Coffee', (.025, .012, .006), .12)
rust = material('Rust seam', (.21, .095, .036), .72)
canvas = material('Faded green canvas', (.12, .23, .20), .88)
glass = material('Tram glass', (.72, .86, .87), .075)
glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 1
glass.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value = 1.45
amber = material('Lantern amber', (1, .51, .17), .3, emission=4)
steel_roof = material('Roof zinc', (.16, .22, .22), .39, .65)


def bevel(obj, amount=.04, segments=3):
    mod = obj.modifiers.new('Rounded manufactured edge', 'BEVEL')
    mod.width = amount
    mod.segments = segments
    obj.modifiers.new('Weighted surface normals', 'WEIGHTED_NORMAL')
    return obj


def box(name, center, size, mat, edge=0):
    points = [(x * size[0] / 2 + center[0], y * size[1] / 2 + center[1], z * size[2] / 2 + center[2])
              for x, y, z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    obj = mesh_object(name, points, [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)], mat)
    return bevel(obj, edge) if edge else obj


def curve(name, points, radius, mat, cyclic=False):
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
    scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def lathe(name, center, profile, mat, segments=32):
    vertices = [(center[0]+r*math.cos(i*2*math.pi/segments), center[1]+r*math.sin(i*2*math.pi/segments), center[2]+z)
                for r,z in profile for i in range(segments)]
    faces = [(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i)
             for j in range(len(profile)-1) for i in range(segments)]
    return mesh_object(name, vertices, faces, mat, True)


def bar(name, start, end, radius, mat):
    # Straight curves avoid operator/dependency-graph overhead for repeated geometry.
    return curve(name, [start, end], radius, mat)


# Tram: shaped shell instead of a rectangular lid, with arched ribs.
remove_prefix('Tram roof', 'Roof seam', 'Tram headlight')
for obj in bpy.data.objects:
    if obj.name.startswith(('Tram lower body', 'Tram chassis')):
        obj.modifiers.clear()
        bevel(obj, .13, 5)
xs = [-1.36 + i*2.72/32 for i in range(33)]
profile = [(3.1+x, 4.10 + .43*math.sqrt(max(0, 1-(x/1.37)**2))) for x in xs]
roof_vertices = [(x, y, z) for y in [2.77, 8.23] for x,z in profile]
roof_faces = [(i,i+1,34+i,33+i) for i in range(32)]
roof = mesh_object('Barrel vault tram roof', roof_vertices, roof_faces, steel_roof, True)
solid = roof.modifiers.new('Roof sheet thickness', 'SOLIDIFY'); solid.thickness = .065
for y in [2.82+i*.48 for i in range(12)]:
    curve('Arched roof seam', [(x,y,z+.025) for x,z in profile[::4]], .017, iron)
for x in [1.75,4.45]:
    bar('Roof rain gutter', (x,2.78,4.12), (x,8.24,4.12), .045, iron)
# Softly rounded window framing and thin solid glass, not empty rectangular gaps.
for side in [1.91,4.29]:
    for ya,yb in [(3.10,4.04),(4.25,5.19),(5.40,6.34),(6.55,7.88)]:
        curve('Rounded tram window frame', [(side,ya+.12,2.94),(side,yb-.12,2.94),(side,yb,3.07),
              (side,yb,3.86),(side,yb-.12,3.98),(side,ya+.12,3.98),(side,ya,3.86),(side,ya,3.07)], .024, cream, True)
        box('Tram glazing', (side,(ya+yb)/2,3.46), (.012,yb-ya-.05,.98), glass)
for xa,xb in [(2.12,3.04),(3.16,4.08)]:
    curve('Rounded front windscreen', [(xa+.1,2.91,2.96),(xb-.1,2.91,2.96),(xb,2.91,3.06),
          (xb,2.91,3.9),(xb-.1,2.91,4.0),(xa+.1,2.91,4.0),(xa,2.91,3.9),(xa,2.91,3.06)],.025,cream,True)
    box('Front glass', ((xa+xb)/2,2.945,3.48), (xb-xa-.06,.012,.96), glass)
    bar('Windscreen wiper', (xa+.13,2.885,2.98), (xb-.15,2.885,3.56), .014, iron)
for x in [2.15,4.05]:
    # Lathed lamp is made on Z then turned toward the camera.
    lamp = lathe('Circular headlamp bezel',(0,0,0),[(0,0),(.16,0),(.17,.035),(.14,.085),(0,.085)],iron)
    lamp.rotation_euler[0]=math.pi/2; lamp.location=(x,2.91,2.03)
    bulb=lathe('Circular headlamp lens',(0,0,0),[(0,0),(.125,0),(.125,.02),(0,.02)],amber)
    bulb.rotation_euler[0]=math.pi/2; bulb.location=(x,2.82,2.03)
curve('Front curved bumper',[(1.94,3.1,1.57),(1.97,2.78,1.57),(2.25,2.70,1.57),(3.95,2.70,1.57),(4.23,2.78,1.57),(4.26,3.1,1.57)],.08,iron)
for y in [3.5,6.7]:
    for x in [2.12,4.08]:
        wheel=lathe('Tram wheel',(0,0,0),[(0,0),(.26,0),(.29,.04),(.29,.13),(.24,.16),(0,.16)],iron)
        wheel.rotation_euler[1]=math.pi/2; wheel.location=(x,y,1.32)

# Give the facade a projecting curved canvas awning and articulated cornice.
awning_vertices=[]
for x in [-5.06,-1.75]:
    for y,z in [(3.02,3.08),(2.72,3.06),(2.38,2.95),(2.05,2.75),(1.91,2.60)]:
        awning_vertices.append((x,y,z))
awning=mesh_object('Curved shop awning',awning_vertices,[(i,i+1,i+6,i+5) for i in range(4)],canvas,True)
awning.modifiers.new('Canvas thickness','SOLIDIFY').thickness=.025
for x in [-5.06,-4.23,-3.40,-2.57,-1.75]:
    curve('Awning curved rib',[(x,3.02,3.07),(x,2.55,3.0),(x,1.91,2.60)],.015,iron)
for i in range(12):
    x=-5.06+i*3.31/12
    curve('Scalloped canvas valance',[(x,1.91,2.60),(x+.138,1.91,2.49),(x+.276,1.91,2.60)],.045,canvas)
box('Cornice lower molding',(-2,2.67,4.28),(8.65,.18,.13),con,.045)
box('Roof coping',(-2,3.08,4.72),(8.85,1.45,.12),con,.055)
for x in [-5.65,-1.45,1.62]:
    box('Facade pilaster',(x,3.08,2.15),(.19,.32,4.22),con,.025)
# Rounded roof equipment gives the station a less rectangular skyline.
lathe('Roof water tank',(-4.25,3.5,4.78),[(0,0),(.48,0),(.55,.12),(.56,.95),(.49,1.07),(.17,1.12),(0,1.12)],steel_roof)
for z in [4.92,5.28,5.68]:
    curve('Tank reinforcing hoop',[(-4.25+.565*math.cos(i*math.tau/16),3.5+.565*math.sin(i*math.tau/16),z) for i in range(16)],.025,iron,True)
curve('Tank supply pipe',[(-4.25,3.5,4.8),(-3.5,3.5,4.79),(-3.3,3.2,4.78),(-3.3,3.2,4.45)],.045,iron)
# Replace the old glowing doorway card with an actual opening and a shallow room.
remove_prefix('Warm doorway', 'Door recess')
wall=bpy.data.objects.get('Station wall')
cutter=box('Temporary doorway cutter',(-.65,3.5,1.45),(1.40,1.4,2.90),con)
cut=wall.modifiers.new('Real recessed doorway','BOOLEAN'); cut.operation='DIFFERENCE'; cut.solver='EXACT'; cut.object=cutter
bpy.context.view_layer.objects.active=wall
bpy.ops.object.modifier_apply(modifier=cut.name)
bpy.data.objects.remove(cutter,do_unlink=True)
plaster=material('Interior warm plaster',(.32,.24,.14),.85)
linen=material('Oatmeal bedding',(.49,.40,.26),.93)
box('Room rear wall',(-.65,5.0,1.45),(1.5,.15,2.9),plaster,.02)
for x in [-1.43,.13]:
    box('Room side wall',(x,4.22,1.45),(.15,1.65,2.9),plaster,.02)
box('Room floor',(-.65,4.15,.025),(1.55,1.7,.1),wood,.02)
box('Bed base',(-.82,4.40,.29),(1.0,1.28,.48),wood,.04)
box('Soft mattress',(-.82,4.40,.59),(1.03,1.3,.19),linen,.08)
box('Rounded pillow',(-.82,4.80,.76),(.72,.32,.17),cream,.075)
box('Folded teal blanket',(-.82,4.06,.73),(1.05,.55,.11),canvas,.035)
box('Door threshold',(-.65,3.0,.09),(1.45,.32,.14),wood,.025)
box('Woven doormat',(-.65,2.35,.09),(1.17,.68,.025),rust,.025)
roomlight=bpy.data.lights.new('Room warm bounce','AREA'); roomlight.energy=65; roomlight.color=(1,.58,.27); roomlight.shape='DISK'; roomlight.size=.8
roomlamp=bpy.data.objects.new('Room warm bounce',roomlight);scene.collection.objects.link(roomlamp);roomlamp.location=(-.65,4.15,2.55)
roomlamp.rotation_euler=(Vector((-.6,3.0,.6))-roomlamp.location).to_track_quat('-Z','Y').to_euler()
# Actual round vessels on the shop shelves.
remove_prefix('Shop jars')
for row,z in enumerate([1.15,1.8,2.45]):
    for i in range(9):
        h=random.uniform(.18,.30); r=random.uniform(.062,.095)
        lathe('Ceramic shop jar',(-4.55+i*.28,2.92,z+.03),[(0,0),(r*.85,0),(r,.04),(r,h*.7),(r*.65,h*.85),(r*.65,h),(0,h)], ceramic if i%3 else cream,24)
# Inhabited table: hollow mug, curved handle, bowl, bottles.
lathe('Table mug',(.80,-.27,1.09),[(0,0),(.09,0),(.105,.025),(.11,.19),(.095,.205),(.079,.19),(.078,.035),(0,.035)],ceramic)
curve('Mug handle',[(.89,-.27,1.25),(1.01,-.27,1.25),(1.02,-.27,1.13),(.89,-.27,1.13)],.02,ceramic)
lathe('Coffee surface',(.80,-.27,1.25),[(0,0),(.079,0)],coffee)
lathe('Fruit bowl',(.25,-.35,1.09),[(0,0),(.09,0),(.20,.08),(.22,.13),(.20,.14),(.17,.08),(0,.04)],cream)
for x,y in [(.22,-.35),(.34,-.35),(.27,-.27)]:
    lathe('Small orange',(x,y,1.19),[(0,0),(.055,.015),(.07,.06),(.045,.115),(0,.12)],rust,20)

# Plants: replace polyhedral blobs and impossible floating pots with supported vessels,
# branching stems and pointed, curved leaves. Seeds keep all variations repeatable.
remove_prefix('Leaves','Plant stem','Cone')
leaf_meshes=[]
for k,mat in enumerate(leaf_mats):
    verts=[(0,0,0),(-.42,.35,.12),(-.32,.78,.16),(0,1,.06),(.32,.78,.16),(.42,.35,.12),(0,.42,.22),(0,.76,.23)]
    mesh=bpy.data.meshes.new('Pointed leaf mesh %d'%k); mesh.from_pydata(verts,[],[(0,1,6),(1,2,7,6),(2,3,7),(3,4,7),(4,5,6,7),(5,0,6)]); mesh.materials.append(mat)
    for face in mesh.polygons: face.use_smooth=True
    leaf_meshes.append(mesh)


def leaf(point, direction, length):
    obj=bpy.data.objects.new('Instanced curved leaf',random.choice(leaf_meshes)); scene.collection.objects.link(obj)
    obj.location=point; obj.rotation_euler=Vector(direction).to_track_quat('Y','Z').to_euler(); obj.scale=(length*.65,length,length)


def potted_plant(x,y,z,s):
    lathe('Supported terracotta planter',(x,y,z),[(0,0),(.17*s,0),(.24*s,.37*s),(.27*s,.38*s),(.27*s,.43*s),(.22*s,.43*s),(.20*s,.36*s),(0,.36*s)],soil)
    for j in range(10):
        angle=j*2.4; reach=random.uniform(.28,.58)*s; h=random.uniform(.60,1.0)*s
        end=Vector((x+math.cos(angle)*reach,y+math.sin(angle)*reach,z+h))
        start=Vector((x,y,z+.35*s)); mid=start.lerp(end,.65)+Vector((0,0,.18*s))
        curve('Arching plant stem',[start,mid,end],.008*s,leaf_mats[0])
        for t in [.45,.7,1.0]:
            pt=start.lerp(end,t); pt.z+=.12*s*math.sin(t*math.pi)
            leaf(pt,(math.cos(angle),math.sin(angle),.25),random.uniform(.2,.36)*s)


for x,y,s in [(-5.2,2,1),(-1.8,2.4,.7),(1.2,2.4,1),(5.4,2.1,1.2),(5.4,.8,.8),(5.4,-2.8,.8),(-5.4,-2.9,.8),(1.8,3.8,.7)]:
    potted_plant(x,y,0,s)
for j in range(20):
    x=random.uniform(-5.7,5.7); y=-4.40; length=random.uniform(.65,2.4)
    pts=[(x,y,.13),(x+.10,y-.07,-.30),(x-.08,y-.05,-length*.6),(x+.12,y,-length)]
    curve('Attached trailing vine',pts,.014,leaf_mats[0])
    for k in range(12):
        t=k/11; px=x+.12*math.sin(t*8); pz=.1-t*length
        leaf((px,y-.06,pz), ((-1 if k%2 else 1)*.7,-.35,-.5),random.uniform(.16,.29))
# Pipes/cables bend naturally; cables sag between real wall anchors.
curve('Bent drainage pipe',[(-5.75,2.80,4.4),(-5.75,2.80,3.0),(-5.80,2.65,2.80),(-5.80,2.65,.2)],.065,iron)
curve('Sagging shop cable',[(-5.8,2.65,3.35),(-3.7,2.30,3.20),(-1.5,2.65,3.35)],.018,iron)
curve('Utility cable terrace',[(-5.8,-4.45,-.65),(0,-4.65,-1.0),(5.8,-4.45,-.65)],.025,iron)
# Stair stringers, guard posts and landing: eliminate floating step silhouettes.
for x in [-8.03,-5.97]:
    bar('Stair structural stringer',(x,-6.2,-3.82),(x,2.4,-.03),.12,iron)
    for i in range(0,20,3):
        y=-6+i*.43; z=-3.5+i*.19
        bar('Stair handrail post',(x,y,z),(x,y,z+1.06),.037,iron)
    bar('Continuous stair handrail',(x,-6,-2.44),(x,2.2,1.18),.046,iron)
box('Stair top landing',(-6.9,2.7,-.04),(2.4,1.1,.28),con,.045)
# Articulate the huge pedestal with floor plates, pilasters, inset windows and braces.
shadow=material('Dark recessed windows',(.025,.055,.065),.26,.25)
for z in [-2.8,-5.7,-8.6,-11.5]:
    box('Tower projecting floor belt',(0,-1.55,z),(11.5,.5,.22),con,.035)
    for x in [-4.9,-2.4,.1,2.6,5.1]:
        box('Tower recessed lower window',(x,-1.53,z+1.35),(1.3,.035,1.75),shadow,.04)
        box('Lower window sill',(x,-1.71,z+.46),(1.45,.38,.12),con,.025)
for x in [-5.2,-1.9,1.9,5.2]:
    box('Tower vertical pilaster',(x,-1.7,-6),(.23,.38,11.8),con,.035)
for x in [-5.2,-1.9,1.9,5.2]:
    bar('Slab knee brace',(x,-1.8,-2.0),(x,-4.1,-.48),.12,iron)

# Rebuild the background as several building families, with stepped silhouettes,
# balconies, roof tanks, antennae and thinner, more numerous windows.
remove_prefix('Distant tower','City window')
random.seed(402)
city_mats=[material('City concrete %d'%i,c,.8) for i,c in enumerate([(.12,.19,.25),(.16,.22,.27),(.19,.25,.28),(.105,.16,.21)])]
city_glow=[material('City lights %d'%i,c,.4,emission=e) for i,(c,e) in enumerate([((.90,.47,.17),2),((.6,.7,.75),1.4),((.95,.66,.35),1.4)])]
# Batch each material's boxes into one mesh to keep the city cheap to generate.
batches={}
def citybox(name,center,size,mat):
    key=mat.name
    if key not in batches: batches[key]=[[],[],mat]
    vs,fs,_=batches[key]; base=len(vs)
    vs.extend([(center[0]+x*size[0]/2,center[1]+y*size[1]/2,center[2]+z*size[2]/2) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]])
    fs.extend([tuple(base+i for i in face) for face in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]])

for row in range(5):
    y=13+row*7
    for col in range(15):
        x=(col-7)*3.1+random.uniform(-.45,.45)
        by=y+random.uniform(-.7,.7); w=random.uniform(1.8,2.7); d=random.uniform(2,3.6)
        h=random.uniform(7,18) if row==0 else random.uniform(10,27)
        base=-15-row*1.3; mat=random.choice(city_mats); family=random.randrange(3)
        citybox('Tower',(x,by,base+h/2),(w,d,h),mat)
        citybox('Roof cornice',(x,by,base+h),(w+.14,d+.14,.16),mat)
        if family!=0:
            citybox('Setback',(x+.12,by+.15,base+h+.65),(w*.65,d*.65,1.3),mat)
        if family==1 and row<3:
            lathe('Rooftop cylindrical tank',(x,by,base+h+1.3),[(0,0),(.36,0),(.36,.85),(.30,1.0),(0,1.0)],iron,16)
            bar('Rooftop aerial',(x+.6,by,base+h),(x+.6,by,base+h+2.5),.024,iron)
        floors=int(h/.68)
        for k in range(1,floors):
            z=base+k*.68
            if family==2 and k%3==0:
                citybox('Balcony',(x,by-d/2-.15,z-.18),(w+.15,.40,.10),mat)
                citybox('Balcony lip',(x,by-d/2-.34,z),(w+.15,.045,.30),city_mats[0])
            for c in range(4):
                wm=random.choice(city_glow) if random.random()<.29 else shadow
                citybox('Front windows',(x-w*.36+c*w*.24,by-d/2-.012,z),(.14,.025,.30),wm)
                if c<3:
                    citybox('Side windows',(x+w/2+.012,by-d*.32+c*d*.29,z),(.025,.17,.30),wm)
for _,(vs,fs,mat) in batches.items(): mesh_object('Batched city '+mat.name,vs,fs,mat)
# A narrow bridge breaks the vertical-only skyline.
for x in [-13,11]:
    box('Distant maintenance bridge',(x,18,-1),(8,1,.18),iron)
    for j in range(9):
        bar('Bridge brace',(x-4+j,17.5,-1),(x-3+j,17.5,.2),.035,iron)
    bar('Bridge top rail',(x-4,17.5,.2),(x+4,17.5,.2),.04,iron)
# Finite haze behind the station, preserving crisp foreground silhouettes.
haze=bpy.data.materials.new('Blue distance haze'); haze.use_nodes=True; nodes=haze.node_tree.nodes; nodes.clear()
out=nodes.new('ShaderNodeOutputMaterial'); volume=nodes.new('ShaderNodeVolumePrincipled')
volume.inputs['Density'].default_value=.012
volume.inputs['Color'].default_value=(.40,.53,.68,1)
volume.inputs['Anisotropy'].default_value=.25
haze.node_tree.links.new(volume.outputs['Volume'],out.inputs['Volume'])
box('Background atmosphere',(0,40,5),(160,64,90),haze)
# Subtler surface micro-relief; do not make metal/wood look like bumpy stone.
for mat in [teal,iron,wood,cream,con]:
    for node in mat.node_tree.nodes:
        if node.type=='BUMP':
            node.inputs['Distance'].default_value=.012 if mat!=con else .035
            node.inputs['Strength'].default_value=.18
# The third pass permits art direction changes, unlike the first comparison.
for obj in scene.objects:
    if obj.type=='LIGHT' and obj.data.type=='AREA':
        if obj.location.z>6: obj.data.energy*=.55
        elif obj.location.y>0: obj.data.energy*=1.65
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.22
cam=scene.camera; cam.location=(14,-20,13)
cam.rotation_euler=(Vector((-.1,1.4,.9))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=46
scene.cycles.samples=args.samples; scene.cycles.use_denoising=False
scene.cycles.max_bounces=10; scene.cycles.transmission_bounces=6
scene.render.resolution_x=1440; scene.render.resolution_y=960; scene.render.resolution_percentage=args.scale
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(ROOT / 'renders/refined.png')
scene.render.threads_mode='FIXED'; scene.render.threads=5
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'scenes/refined.blend'))
bpy.ops.render.render(write_still=True)
