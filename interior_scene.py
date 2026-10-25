"""Fourth pass: real station volume, connected interior and lower exterior views."""
import argparse
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from blender_shapes import area_light, box, curve, lathe, material, text

parser = argparse.ArgumentParser()
parser.add_argument('--samples', type=int, default=96)
parser.add_argument('--scale', type=int, default=100)
parser.add_argument('--view', choices=['left', 'front', 'detail', 'all'], default='left')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'scenes/refined.blend'))
scene = bpy.context.scene
random.seed(129)

# Remove the thin facade, shallow bedroom, and front-mounted shelves that hid depth.
prefixes = ('Station wall', 'Shop recess', 'Window frame', 'Window sill', 'Shop shelving',
            'Ceramic shop jar', 'Counter', 'Open teal door', 'Room ', 'Bed base', 'Soft mattress',
            'Rounded pillow', 'Folded teal blanket', 'Door threshold', 'Woven doormat',
            'Roof cornice', 'Roof coping', 'Cornice lower molding', 'Facade pilaster')
for obj in list(bpy.data.objects):
    if obj.name.startswith(prefixes):
        bpy.data.objects.remove(obj, do_unlink=True)
con = bpy.data.materials['Stained concrete']
wood = bpy.data.materials['Aged timber']
teal = bpy.data.materials['Oxidized teal paint']
iron = bpy.data.materials['Old steel']
cream = bpy.data.materials['Ivory enamel']
ceramic = bpy.data.materials['Glazed moss ceramic']
canvas = bpy.data.materials['Faded green canvas']
plaster = material('Station lime plaster', (.38, .34, .25), .87)
walltile = material('Old green glazed tile', (.12, .22, .18), .29)
linen = material('Bench fabric', (.25, .29, .23), .93)
black = material('Chalkboard', (.024, .045, .038), .85)
paper = material('Old timetable paper', (.63, .57, .40), .82)
steel = material('Kitchen stainless steel', (.34, .39, .38), .27, .75)
lampmat = material('Warm lamp diffusers', (1, .65, .31), .32, emission=3)
floor_mats = [material('Interior tile %d' % i, (.21+i*.018,.19+i*.015,.14+i*.013), .4) for i in range(5)]
# Actual floor, enclosing side/rear walls and continuous roof (not a cutaway).
box('Station floor slab', (-2.3,5.72,-.02), (7.9,5.5,.27), con, .035)
for ix in range(18):
    for iy in range(12):
        box('Interior floor tile', (-5.79+ix*.40,3.39+iy*.40,.13),(.391,.391,.035),random.choice(floor_mats))
box('Station full roof slab', (-2.3,5.7,4.46), (8.2,5.9,.30), con, .045)
box('Interior ceiling', (-2.3,5.7,4.27), (7.6,5.25,.10), plaster)
for y in [3.65,5.15,6.65,8.1]:
    box('Exposed ceiling joist', (-2.3,y,4.12), (7.55,.18,.24), wood, .025)
# Front openings assembled with structural piers: no Boolean surface cards.
for x,w in [(-5.86,.32),(-1.86,.40),(1.0,.80)]:
    box('Station front pier',(x,3.25,2.2),(w,.42,4.4),con,.035)
box('Front lintel',(-2.3,3.25,3.9),(7.7,.42,1.0),con,.035)
box('Shop front knee wall',(-3.88,3.25,.45),(3.64,.42,.90),con,.025)
box('Shop deep stone sill',(-3.88,3.15,.96),(3.75,.68,.13),cream,.025)
# Left return has a long clear window, revealing the side and the room depth.
for y,d in [(3.55,.60),(7.95,.65)]:
    box('Left return pier',(-6.02,y,2.2),(.32,d,4.4),con,.035)
box('Left window lower wall',(-6.02,5.65,.48),(.32,3.65,.96),con,.025)
box('Left return lintel',(-6.02,5.65,3.88),(.32,3.65,1.04),con,.025)
box('Left side window sill',(-6.08,5.65,1.0),(.55,3.8,.13),cream,.025)
sideglass=material('Station clear side glass',(.92,.97,.96),.035)
bsdf=sideglass.node_tree.nodes['Principled BSDF']; bsdf.inputs['Transmission Weight'].default_value=1;bsdf.inputs['IOR'].default_value=1.45
for ya,yb in [(3.88,5.0),(5.10,6.22),(6.32,7.44)]:
    box('Side window glass',(-6.035,(ya+yb)/2,2.18),(.009,yb-ya,2.22),sideglass)
    box('Side window mullion',(-6.10,ya,2.16),(.12,.065,2.30),teal,.012)
box('Side window head',(-6.10,5.65,3.30),(.12,3.8,.10),teal,.012)
# Solid right return; rear exit is real and connects to a small platform landing.
box('Right return wall',(1.39,5.75,2.2),(.30,5.3,4.4),con,.035)
box('Rear cafe wall',(-3.8,8.30,2.2),(4.65,.28,4.4),plaster,.02)
box('Rear exit right pier',(.99,8.30,2.2),(.80,.28,4.4),plaster,.02)
box('Rear exit lintel',(-.42,8.30,3.70),(2.0,.28,1.4),plaster,.02)
box('Platform exit landing',(.30,8.85,.10),(3.5,1.2,.23),con,.025)
box('Outer roof front molding',(-2.3,2.94,4.56),(8.3,.24,.18),con,.045)
box('Outer roof left molding',(-6.37,5.70,4.56),(.24,5.65,.18),con,.045)
# A shallower awning preserves shelter without blocking the view to rear shelves.
for obj in list(scene.objects):
    if obj.name.startswith(('Curved shop awning','Awning curved rib','Scalloped canvas valance')):
        bpy.data.objects.remove(obj,do_unlink=True)
awning_mesh=bpy.data.meshes.new('Short canvas awning mesh')
awning_mesh.from_pydata([(x,y,z) for x in [-5.77,-2.17] for y,z in [(3.04,3.28),(2.86,3.27),(2.63,3.18)]],[],[(0,1,4,3),(1,2,5,4)])
awning_mesh.materials.append(canvas)
awning=bpy.data.objects.new('Short continuous canvas canopy',awning_mesh);scene.collection.objects.link(awning)
awning.modifiers.new('Canvas sheet thickness','SOLIDIFY').thickness=.02
for i in range(18):
    x=-5.67+i*.20
    if i%2==0:
        curve('Retracted canvas awning rib',[(x,3.04,3.29),(x,2.86,3.28),(x,2.63,3.19)],.009,teal)
    curve('Retracted canvas scallop',[(x-.10,2.63,3.18),(x,2.63,3.10),(x+.10,2.63,3.18)],.018,canvas)
# Roof tank and supply pipe move onto the full roof, away from the front silhouette.
for obj in scene.objects:
    if obj.name.startswith(('Roof water tank','Tank reinforcing hoop','Tank supply pipe')):
        obj.location.y += 2.35
        obj.location.z -= .12
# Teal door is genuinely swung outward around its hinge, clear of the entrance.
hinge=bpy.data.objects.new('Entrance door hinge',None);scene.collection.objects.link(hinge)
hinge.location=(.57,3.02,.14);hinge.rotation_euler.z=math.radians(103)
door=box('Swung open entrance door',(0,0,0),(1.85,.11,2.90),teal,.035);door.parent=hinge;door.location=(-.925,0,1.45)
handle=curve('Entrance curved handle',[(-1.62,-.10,1.20),(-1.62,-.16,1.24),(-1.62,-.16,1.43),(-1.62,-.10,1.47)],.023,cream);handle.parent=hinge
box('Broad entry threshold',(-.52,3.20,.15),(2.15,.65,.13),wood,.025)
box('Entry woven mat',(-.52,2.32,.11),(1.45,.85,.025),canvas,.015)
# A service counter sits just inside; the aisle and rear counter are separate layers.
box('Cafe front cabinet',(-4.18,3.78,.65),(2.8,.68,.98),teal,.03)
box('Cafe timber worktop',(-4.18,3.76,1.19),(3.0,.87,.13),wood,.04)
for x in [-5.08,-4.2,-3.32]:
    box('Cabinet front panel',(x,3.42,.68),(.78,.06,.75),wood,.025)
    curve('Cabinet handle',[(x-.10,3.36,.94),(x+.10,3.36,.94)],.015,iron)
# Back counter is far enough behind to produce visible floor space and parallax.
box('Cafe backbar cabinet',(-4.25,6.90,.69),(2.90,.70,1.08),teal,.025)
box('Backbar worktop',(-4.25,6.90,1.27),(3.1,.85,.13),cream,.025)
for z in [1.65,2.28,2.91]:
    box('Rear cafe shelf',(-4.10,8.04,z),(3.50,.42,.075),wood,.015)
    for i in range(11):
        h=random.uniform(.19,.33);r=random.uniform(.055,.09)
        lathe('Rear shelf vessel',(-5.62+i*.29,7.99,z+.04),[(0,0),(r,0),(r,h*.7),(r*.62,h*.87),(r*.62,h),(0,h)],ceramic if i%3 else cream,24)
# Secondary wall and deeper passage provide a visible sequence of rooms.
box('Cafe rear partition',(-2.17,7.15,1.75),(.15,2.1,3.35),plaster,.02)
box('Passage left pier',(-1.30,6.60,1.70),(.22,.24,3.1),wood,.025)
box('Passage right pier',(.58,6.60,1.70),(.22,.24,3.1),wood,.025)
box('Passage lintel',(-.36,6.60,3.23),(2.10,.24,.22),wood,.025)
text('PLATFORM  02',(-1.14,6.44,3.20),.14,cream)
# Espresso machine, stacked cups and sink have recognizable dimensions.
box('Espresso machine',(-4.92,6.78,1.57),(.82,.52,.52),steel,.065)
box('Espresso dark face',(-4.92,6.495,1.58),(.69,.035,.32),iron,.035)
for x in [-5.12,-4.83]:
    curve('Espresso group handle',[(x,6.46,1.52),(x,6.30,1.47),(x+.13,6.30,1.47)],.018,iron)
    lathe('Espresso cup',(x,6.43,1.34),[(0,0),(.065,0),(.08,.10),(.06,.12),(.045,.03),(0,.03)],cream,24)
lathe('Kitchen sink',(-3.35,6.83,1.32),[(0,-.13),(.20,-.10),(.26,.0),(.27,.03),(.24,.04),(.19,-.07),(0,-.09)],steel)
curve('Gooseneck tap',[(-3.35,7.13,1.34),(-3.35,7.13,1.73),(-3.35,6.97,1.81),(-3.35,6.84,1.67)],.024,steel)
# Menu and frames are mounted on real surfaces inside, not across exterior openings.
box('Cafe menu board',(-3.86,8.11,3.48),(2.0,.07,.73),black,.025)
text('SUMMIT CAFE\nTEA  /  COFFEE  /  NOODLES',(-4.75,8.06,3.66),.115,paper)
box('Station timetable board',(.87,7.98,2.24),(.60,.06,1.15),wood,.025)
box('Station timetable paper',(.87,7.94,2.24),(.48,.015,1.0),paper)
text('DEPARTURES\n06:30\n07:00\n07:30\n08:00',(.66,7.92,2.58),.085,iron)
# Waiting bench along right wall leaves the entry/passage sightline unobstructed.
for i in range(4):
    box('Waiting bench plank',(.94,5.22,.66+i*.055),(.57,1.80,.045),wood,.015)
box('Waiting bench back',(1.09,5.22,1.16),(.12,1.82,.58),wood,.025)
for y in [4.52,5.92]:
    box('Waiting bench leg',(.91,y,.40),(.45,.12,.55),iron,.015)
# A round tea table and two stools occupy the cafe side, away from the passage.
lathe('Interior tea tabletop',(-2.72,5.08,.93),[(0,0),(.40,0),(.42,.05),(.39,.10),(0,.10)],wood)
lathe('Tea table pedestal',(-2.72,5.08,.17),[(0,0),(.24,0),(.27,.04),(.07,.10),(.055,.78),(0,.78)],iron)
for x,y in [(-3.48,5.06),(-2.75,5.88)]:
    lathe('Cafe stool seat',(x,y,.67),[(0,0),(.23,0),(.25,.055),(.21,.10),(0,.10)],wood)
    for dx,dy in [(-.13,-.13),(.13,-.13),(-.13,.13),(.13,.13)]:
        curve('Cafe stool leg',[(x+dx*1.35,y+dy*1.35,.17),(x+dx,y+dy,.69)],.028,iron)
# A wall-mounted network map adds scale and gives the waiting area a purpose.
box('Platform route map frame',(1.20,5.28,2.45),(.10,1.40,.95),wood,.025)
box('Platform route map paper',(1.138,5.28,2.45),(.015,1.28,.83),paper)
route=material('Faded route red',(.38,.10,.055),.8)
curve('Station route diagram',[(1.122,4.80,2.18),(1.122,5.0,2.34),(1.122,5.24,2.34),(1.122,5.44,2.56),(1.122,5.72,2.68)],.015,route)
for y,z in [(4.80,2.18),(5.0,2.34),(5.24,2.34),(5.44,2.56),(5.72,2.68)]:
    curve('Route map stop',[(1.115,y+.035*math.cos(i*math.tau/12),z+.035*math.sin(i*math.tau/12)) for i in range(12)],.009,iron,True)
# A hanging fern near the side return reinforces the interior/window parallax.
lathe('Hanging ceramic pot',(-5.55,4.6,2.65),[(0,0),(.14,0),(.20,.26),(.18,.28),(.15,.25),(0,.05)],ceramic)
for dx,dy in [(-.13,0),(.13,0),(0,.13)]:
    curve('Fern suspension cord',[(-5.55+dx,4.6+dy,2.90),(-5.55,4.6,4.08)],.007,iron)
leaf_mesh=bpy.data.meshes.get('Pointed leaf mesh 1')
if leaf_mesh:
    for i in range(25):
        angle=i*2.4;t=i/25
        obj=bpy.data.objects.new('Interior fern leaf',leaf_mesh);scene.collection.objects.link(obj)
        obj.location=(-5.55+.16*math.cos(angle),4.6+.16*math.sin(angle),2.90)
        obj.rotation_euler=Vector((math.cos(angle),math.sin(angle),.15-t)).to_track_quat('Y','Z').to_euler();obj.scale=(.20,.35+.10*t,.30)
# Pendant shades and separate front/rear light pools retain shadow between layers.
for x,y,power in [(-4.5,4.65,145),(-4.1,7.25,110),(-.35,5.35,130)]:
    curve('Pendant cord',[(x,y,4.18),(x,y,3.38)],.012,iron)
    lathe('Enamel pendant shade',(x,y,3.22),[(.30,0),(.29,.045),(.10,.23),(.065,.25)],teal)
    lathe('Pendant diffuser',(x,y,3.22),[(0,0),(.26,0)],lampmat)
    area_light('Interior pendant',(x,y,3.20),power,(1,.65,.33),.58,(x,y,.4))
area_light('Rear passage blue fill',(-.35,8.14,2.55),48,(.43,.65,.95),1.1,(-.4,4.0,1.0))
area_light('Rear shelf warm wash',(-4.0,7.72,3.5),95,(1,.60,.30),1.4,(-4,8.1,1.7))
# Camera candidates share geometry and lighting. Full roof stays present in all views.
views={
    'left':((-16,-19,8.0),(-.10,3.0,1.10),45),
    'front':((-3.4,-21,6.2),(-.25,3.4,1.30),45),
    'detail':((-3.5,-8.5,3.6),(-2.3,5.4,1.75),43),
}
cam=scene.camera
scene.cycles.samples=args.samples;scene.cycles.use_denoising=False
scene.render.resolution_x=1440;scene.render.resolution_y=960;scene.render.resolution_percentage=args.scale
scene.render.threads=5;scene.render.threads_mode='FIXED'
for view in (views if args.view=='all' else [args.view]):
    location,target,lens=views[view];cam.location=location
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    filename='interior' if view=='left' else 'interior-'+view
    scene.render.filepath=str(ROOT/'renders'/f'{filename}.png')
    if args.scale==100 and args.view!='all':
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scenes'/f'{filename}.blend'),compress=True)
    bpy.ops.render.render(write_still=True)
