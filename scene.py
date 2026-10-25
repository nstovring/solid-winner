import bpy, math, random, argparse, sys
from mathutils import Vector
p=argparse.ArgumentParser(); p.add_argument('--stage',choices=['baseline','improved'],default='improved'); p.add_argument('--samples',type=int,default=48); a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
rich=a.stage=='improved'; random.seed(24)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,col,metal=0,rough=.6):
 m=bpy.data.materials.new(name); m.diffuse_color=(*col,1); m.use_nodes=True; n=m.node_tree.nodes; b=n.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*col,1); b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
 if rich:
  tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=5; tex.inputs['Detail'].default_value=4
  ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.25; ramp.color_ramp.elements[0].color=(*[v*.28 for v in col],1); ramp.color_ramp.elements[1].position=.75; ramp.color_ramp.elements[1].color=(*col,1)
  m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs[0]); m.node_tree.links.new(ramp.outputs[0],b.inputs['Base Color'])
  bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.25; bump.inputs['Distance'].default_value=.07; m.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height']); m.node_tree.links.new(bump.outputs[0],b.inputs['Normal'])
 return m
def glow(name,col,strength):
 m=mat(name,col); b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Emission Color'].default_value=(*col,1); b.inputs['Emission Strength'].default_value=strength; return m
con=mat('Stained concrete',(.29,.31,.29)); floor=mat('Rain darkened paving',(.24,.27,.26),.15,.22 if rich else .65); teal=mat('Oxidized teal paint',(.045,.20,.19),.5); iron=mat('Old steel',(.10,.13,.14),.75,.34); wood=mat('Aged timber',(.24,.12,.055)); cream=mat('Ivory enamel',(.72,.64,.43)); leaf=mat('Leaves',(.075,.18,.065)); soil=mat('Terracotta',(.25,.13,.075)); dark=mat('Interior darkness',(.018,.026,.026)); warm=glow('Amber lamps',(1,.48,.12),4); window=glow('Occupied city windows',(.95,.51,.19),1.7); cool=mat('Distant blue concrete',(.12,.20,.29))
def box(name,loc,size,m,bev=.025):
 verts=[(x*size[0]/2,y*size[1]/2,z*size[2]/2) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]); mesh.update(); o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.location=loc; o.data.materials.append(m)
 if rich and bev:
  mod=o.modifiers.new('Worn edges','BEVEL'); mod.width=bev; mod.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def rod(name,start,end,r,m):
 d=Vector(end)-Vector(start); bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=d.length,location=(Vector(start)+Vector(end))/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o
def text(body,loc,size,m):
 bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=body; o.data.body=body; o.data.size=size; o.data.extrude=.001; o.data.materials.append(m)
def light(loc,power,color,size=1,target=None):
 bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size
 if target: o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
# Elevated station terrace, exposed slab and supporting tower.
box('Tower',(0,2,-7),(11,7,14),con); box('Terrace slab',(0,0,-.25),(12,9,.5),con)
for x in range(-6,6):
 for y in range(-4,5): box('Individual paving slab',(x+.5,y-.5,.015),(.975,.975,.08),floor,.012)
# Facade with open shop and doorway.
box('Station wall',(-2,3.5,2.2),(8,.5,4.4),con); box('Roof cornice',(-2,3.1,4.5),(8.6,1.4,.35),con)
box('Shop recess',(-3.4,3.20,1.8),(2.8,.12,2.1),dark); box('Door recess',(-.6,3.19,1.5),(1.5,.12,2.9),dark)
for x in [-4.85,-1.95]: box('Window frame',(x,3.05,1.8),(.10,.19,2.3),cream)
for z in [.72,2.88]: box('Window sill',(-3.4,3.02,z),(3.1,.42,.11),wood)
for z in [1.15,1.8,2.45]:
 box('Shop shelving',(-3.4,3.02,z),(2.7,.34,.065),wood)
 for i in range(9): box('Shop jars',(-4.55+i*.28,2.99,z+.14),(.15,.15,.23),cream if i%3 else teal,.015)
box('Counter',(-3.4,2.75,.95),(3.1,.8,.14),wood)
box('Open teal door',(.18,2.83,1.45),(.63,.18,2.85),teal)
box('Warm doorway',(-.7,3.09,1.6),(1.05,.04,2.5),glow('Interior wall',(.55,.26,.08),.65))
box('Sign backing',(-2.4,3.02,3.66),(6.8,.18,.74),cream)
text('SUMMIT FUNICULAR STATION',(-5.48,2.91,3.69),.265,dark); text('DECOMMISSIONED  /  UPPER TERMINUS',(-5.45,2.90,3.41),.13,dark)
# Stair flight at left.
for i in range(20):
 z=-3.5+i*.19; y=-6+i*.43
 box('Concrete stair',(-7,y,z),(2.2,.47,.25),con)
rod('Stair handrail',(-8.05,-6,-2.5),(-8.05,2.4,1.2),.045,iron)
# Terrace handrail.
for start,end in [((-5.9,-4.3,0),(5.9,-4.3,0)),((5.9,-4.3,0),(5.9,3.7,0)),((-5.9,-4.3,0),(-5.9,1.5,0))]:
 s,e=Vector(start),Vector(end); rod('Handrail',s+Vector((0,0,1.15)),e+Vector((0,0,1.15)),.055,iron); rod('Lower rail',s+Vector((0,0,.2)),e+Vector((0,0,.2)),.035,iron)
 for i in range(int((e-s).length/.36)+1):
  v=s+(e-s)*i/int((e-s).length/.36); rod('Railing baluster',v,v+Vector((0,0,1.15)),.025,iron)
# Timber communal table.
for i in range(6): box('Table plank',(.1,-.7+i*.17,1.02),(2.8,.16,.12),wood)
for x in [-1,1.1]:
 for y in [-.6,.15]: box('Table leg',(x,y,.52),(.14,.14,1),wood)
for y in [-1.2,.75]:
 box('Bench seat',(.1,y,.57),(2.9,.32,.12),wood)
 for x in [-1,1.1]: box('Bench leg',(x,y,.27),(.14,.23,.54),wood)
box('Laptop keyboard',(-.5,-.23,1.12),(.58,.43,.04),iron); screen=box('Laptop display',(-.5,.0,1.34),(.58,.045,.42),dark)
for i in range(7): box('Terminal text',(-.55,.0-.026,1.20+i*.036),(.35 if i%2 else .44,.006,.009),glow('Terminal cyan'+str(i),(.2,.7,.7),1))
# Funicular on the right, raised behind terrace.
for x in [2.2,4.0]:
 rod('Rail',(x,1.4,.35),(x,9,2.0),.07,iron)
for y in [1.6+i*.4 for i in range(18)]: box('Rail sleeper',(3.1,y,.3+(y-1.4)*.217),(2.5,.16,.14),wood)
box('Tram chassis',(3.1,5.5,1.65),(2.5,5.3,.45),iron); box('Tram lower body',(3.1,5.5,2.25),(2.4,5.1,1.05),teal)
box('Tram roof',(3.1,5.5,4.28),(2.65,5.4,.27),con)
for x in [1.9,4.3]:
 for y in [3.0,4.15,5.3,6.45,8.0]: box('Tram window pillar',(x,y,3.45),(.09,.09,1.6),cream)
 box('Window top beam',(x,5.5,4.08),(.12,5.1,.12),cream)
 box('Window lower beam',(x,5.5,2.84),(.12,5.1,.1),cream)
for x in [2.05,3.1,4.15]: box('Front windscreen post',(x,2.96,3.45),(.08,.10,1.6),cream)
box('Tram lit interior',(3.1,5.5,4.03),(2.1,4.7,.04),warm)
for y in [3.8,5.0,6.2,7.4]:
 box('Tram bench',(3.9,y,2.83),(.55,.78,.22),wood); box('Seat back',(4.1,y,3.1),(.16,.78,.55),wood)
text('02',(2.8,2.90,2.05),.48,cream)
for x in [2.15,4.05]: box('Tram headlight',(x,2.90,1.98),(.22,.08,.18),warm)
# Practical lanterns and facade utility lines.
for x,z in [(-5.5,2.6),(.7,2.6),(5.6,.5),(-5.7,-1.4)]:
 box('Lantern frame',(x,2.72,z),(.22,.25,.42),iron); box('Lantern glass',(x,2.55,z),(.14,.09,.28),warm)
 light((x,2.1,z),85,(1,.48,.16),.6,(x,0,0))
light((-3,2.4,2.1),160,(1,.55,.22),2,(-3,0,1)); light((3.1,4.6,3.8),130,(1,.57,.26),2,(3.1,3,1))
for z in [3.0,4.25]: rod('Facade pipe',(-6,2.91,z),(1.7,2.91,z),.045,iron)
rod('Downpipe',(1.25,2.89,.2),(1.25,2.89,4.4),.065,iron)
# Pots and foliage with deterministic variation.
def plant(x,y,z,scale=1):
 bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=.17*scale,radius2=.25*scale,depth=.4*scale,location=(x,y,z+.2*scale)); bpy.context.object.data.materials.append(soil)
 for j in range(9 if rich else 3):
  dx=random.uniform(-.35,.35)*scale; dy=random.uniform(-.35,.35)*scale; top=(x+dx,y+dy,z+random.uniform(.55,1.1)*scale)
  rod('Plant stem',(x,y,z+.35*scale),top,.012*scale,leaf)
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.18*scale,location=top); o=bpy.context.object; o.name='Leaves'; o.scale=(1,.5,1.7); o.data.materials.append(leaf)
for x,y,s in [(-5.2,2,1),(-1.8,2.4,.7),(1.2,2.4,1),(5.4,2.1,1.2),(5.4,.8,.8),(5.4,-2.8,.8),(-5.4,-2.9,.8),(1.8,3.8,.7)]: plant(x,y,0,s)
if rich:
 for i in range(28): plant(random.uniform(-5.8,5.8),random.choice([4.0,-4.35]),random.choice([-.6,-1.1,-2]),.5)
 # Surface debris, roof seams and irregular paint loss.
 for i in range(65):
  x=random.uniform(1.91,4.29); z=random.uniform(1.9,2.7); box('Tram paint chip',(x,2.938,z),(random.uniform(.015,.11),.008,random.uniform(.015,.09)),wood,0)
 for y in [3.0+i*.45 for i in range(12)]: box('Roof seam',(3.1,y,4.43),(2.6,.025,.03),iron,.008)
 for i in range(30): box('Paving litter',(random.uniform(-5,5),random.uniform(-4,2),.075),(.07,.12,.008),wood,0)
# City drops away behind elevated station.
random.seed(400)
for i in range(65):
 x=random.uniform(-21,23); y=random.uniform(12,38); h=random.uniform(5,23); z=-12+h/2
 w=random.uniform(1.1,2.6); d=random.uniform(1.2,2.6)
 box('Distant tower',(x,y,z),(w,d,h),cool,.035)
 for k in range(int(h/.75)):
  for col in range(3):
   if random.random()<.47: box('City window',(x-w*.32+col*w*.32,y-d/2-.015,-12+k*.75),(.13,.025,.23),window,0)
# Lighting and camera.
world=bpy.data.worlds.new('Blue hour'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.25,.40,1); world.node_tree.nodes['Background'].inputs[1].default_value=.35
light((-4,-1,12),1800,(.43,.61,1),10,(0,1,0)); light((1,-8,7),650,(.49,.66,1),8,(0,2,1))
bpy.ops.object.camera_add(location=(17,-24,17)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,2,1))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='PERSP'; cam.data.lens=43; bpy.context.scene.camera=cam
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=a.samples; sc.cycles.use_denoising=False; sc.render.resolution_x=1200; sc.render.resolution_y=850; sc.render.resolution_percentage=100; sc.render.threads_mode='FIXED'; sc.render.threads=5; sc.view_settings.view_transform='AgX'
sc.render.image_settings.file_format='PNG'; sc.render.filepath='//../renders/'+a.stage+'.png'
bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath('//scenes/'+a.stage+'.blend')); sc.render.filepath=bpy.path.abspath('//../renders/'+a.stage+'.png'); bpy.ops.render.render(write_still=True)
