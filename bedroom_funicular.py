"""LAST STOP: standalone, editable funicular bedroom built without external assets."""
import argparse
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from blender_shapes import box, curve, lathe, material, text, area_light
from bedroom_props import add_bedroom_props

p=argparse.ArgumentParser()
p.add_argument('--view',choices=['hero','entry','cutaway','all'],default='all')
p.add_argument('--samples',type=int,default=96)
p.add_argument('--scale',type=int,default=100)
p.add_argument('--neon-off',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
random.seed(82)
collections={}
for name in ['01_Undercarriage','02_Shell','03_Removable_roof','04_Glazing','05_Interior','06_Textiles','07_Props','08_Lighting','09_Presentation']:
    col=bpy.data.collections.new(name);scene.collection.children.link(col);collections[name]=col

def checkpoint(): return set(bpy.data.objects)
def group(before,name):
    for obj in set(bpy.data.objects)-before:
        for col in list(obj.users_collection): col.objects.unlink(obj)
        collections[name].objects.link(obj)
def mesh(name,verts,faces,mat,smooth=False):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);data.materials.append(mat)
    for poly in data.polygons: poly.use_smooth=smooth
    return obj

def textured(name,color,rough,metal=0,scale=18,bump=.002):
    m=material(name,color,rough,metal);n=m.node_tree.nodes;l=m.node_tree.links;b=n['Principled BSDF']
    tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=3
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*[c*.65 for c in color],1);ramp.color_ramp.elements[1].color=(*color,1)
    l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],b.inputs['Base Color'])
    bn=n.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.18;bn.inputs['Distance'].default_value=bump;l.new(tex.outputs['Fac'],bn.inputs['Height']);l.new(bn.outputs[0],b.inputs['Normal'])
    return m

m={
 'teal':textured('Faded petrol enamel',(.045,.20,.18),.4,.45),
 'iron':textured('Blackened repair steel',(.07,.085,.09),.35,.75),
 'cream':textured('Aged ivory enamel',(.67,.60,.42),.37,.15),
 'wood':textured('Warm plywood',(.36,.20,.085),.55,scale=6,bump=.001),
 'fabric':textured('Oxblood quilt',(.27,.045,.075),.93,scale=230,bump=.001),
 'linen':textured('Oatmeal linen',(.64,.53,.36),.95,scale=260,bump=.0008),
 'accent':textured('Mustard repairs',(.48,.29,.07),.82,scale=150,bump=.001),
 'amber':material('Warm fixture glow',(1,.57,.22),.3,emission=3),
 'glass':material('Clear carriage glass',(.94,.98,.96),.035),
}
m['glass'].node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=1
m['glass'].node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.45
rubber=material('Compressed black rubber',(.012,.019,.019),.75)
roofmat=textured('Weathered zinc roof',(.17,.22,.23),.42,.65,scale=30,bump=.001)
rust=textured('Exposed red primer',(.29,.105,.047),.8,scale=35,bump=.003)
curtainmat=textured('Olive curtain weave',(.17,.21,.12),.98,scale=260,bump=.0009)
patchmats=[m['fabric'],textured('Faded quilt patch',(.37,.11,.13),.95,scale=220,bump=.001),textured('Dark quilt patch',(.16,.035,.055),.95,scale=240,bump=.001),m['accent']]
pink=material('Magenta sign tubing',(1,.045,.25),.3,emission=3 if not a.neon_off else 0)
cyan=material('Cyan step diffuser',(.05,.65,.72),.3,emission=2 if not a.neon_off else 0)

# Straight spans and sampled quarter arcs keep window frames manufactured.
def rounded_loop(name,center,width,height,radius,tube,mat,plane='front'):
    points=[]
    for cx,cz,angle in [(width/2-radius,height/2-radius,0),(-width/2+radius,height/2-radius,90),(-width/2+radius,-height/2+radius,180),(width/2-radius,-height/2+radius,270)]:
        for j in range(7):
            t=math.radians(angle+j*90/6);u=cx+radius*math.cos(t);v=cz+radius*math.sin(t)
            points.append((center[0]+u,center[1],center[2]+v) if plane=='front' else (center[0],center[1]+u,center[2]+v))
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=tube;data.bevel_resolution=3
    sp=data.splines.new('POLY');sp.points.add(len(points)-1)
    for pt,co in zip(sp.points,points):pt.co=(*co,1)
    sp.use_cyclic_u=True
    ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);data.materials.append(mat);return ob

def side_text(body,loc,size,mat):
    ob=text(body,loc,size,mat);ob.rotation_euler=(math.pi/2,0,math.pi/2);return ob

# Fixed running gear, short rail section, real supports under the leveled floor.
before=checkpoint()
for x in [-.78,.78]:
    box('Rail head',(x,2.55,-.80),(.075,6.1,.07),m['iron'],.015)
    box('Rail base',(x,2.55,-.88),(.16,6.1,.035),m['iron'],.01)
for y in [-.3+i*.43 for i in range(15)]:box('Timber rail sleeper',(0,y,-.95),(2.35,.16,.12),m['wood'],.015)
box('Main chassis',(0,2.55,-.04),(2.18,5.05,.25),m['iron'],.055)
for y in [.85,4.20]:
    box('Bogie beam',(0,y,-.35),(2.0,.62,.24),m['iron'],.04)
    curve('Axle', [(-1.10,y,-.53),(1.10,y,-.53)],.075,m['iron'])
    for x in [-.94,.94]:
        wheel=lathe('Flanged steel wheel',(0,0,0),[(0,0),(.23,0),(.27,.025),(.27,.08),(.225,.10),(.225,.20),(0,.20)],m['iron'])
        wheel.rotation_euler.y=math.pi/2;wheel.location=(x-.10,y,-.53)
        for offset in [-.16,.16]:
            lathe('Suspension spring',(x,y+offset,-.31),[(.07,0),(.085,.02),(.07,.04),(.085,.06),(.07,.08),(.085,.10),(.07,.12)],m['iron'],24)
for y in [.4,1.5,2.6,3.7,4.8]:box('Floor crossmember',(0,y,.04),(2.18,.13,.14),m['iron'],.015)
group(before,'01_Undercarriage')

# Thick shell, open window bays and an unobstructed side entry.
before=checkpoint()
box('Leveled floor insert',(0,2.55,.14),(2.24,4.98,.16),m['wood'],.035)
box('Front lower body',(0,.04,.64),(2.38,.17,.88),m['teal'],.11)
box('Rear lower body',(0,5.04,.64),(2.38,.17,.88),m['teal'],.11)
for x in [-1.14,1.14]:
    spans=[(.10,5.0)] if x<0 else [(.10,1.58),(2.58,5.0)]
    for start,end in spans:
        box('Lower side body',(x,(start+end)/2,.64),(.13,end-start,.88),m['teal'],.045)
        box('Interior plywood dado',(x*.947,(start+end)/2,.66),(.045,end-start-.04,.74),m['wood'],.015)
    for y in ([.10,1.43,2.62,3.82,5.0] if x<0 else [.10,1.53,2.63,3.82,5.0]):
        box('Structural window post',(x,y,1.68),(.12,.10,1.26),m['cream'],.025)
    box('Upper side header',(x,2.55,2.28),(.15,5.02,.16),m['teal'],.035)
    box('Lower window belt',(x,2.55,1.10),(.16,5.02,.10),m['cream'],.025)
# Remove the belt across the doorway by replacing right-hand continuous bar.
for ob in list(scene.objects):
    if ob.name.startswith('Lower window belt') and ob.location.x>0:
        bpy.data.objects.remove(ob,do_unlink=True)
for ya,yb in [(.08,1.58),(2.58,5.02)]:box('Right window belt',(1.14,(ya+yb)/2,1.10),(.16,yb-ya,.10),m['cream'],.025)
for y in [.04,5.04]:
    for x in [-1.09,0,1.09]:box('Cab end pillar',(x,y,1.67),(.10,.15,1.24),m['cream'],.03)
    box('Cab top header',(0,y,2.25),(2.30,.16,.16),m['teal'],.04)
    box('Cab window lower beam',(0,y,1.10),(2.30,.18,.11),m['cream'],.03)
for x in [-.83,.83]:
    housing=lathe('Round headlight housing',(0,0,0),[(0,0),(.16,0),(.18,.04),(.17,.13),(.14,.15),(0,.15)],m['iron'])
    housing.rotation_euler.x=math.pi/2;housing.location=(x,-.07,.64)
    lens=lathe('Round headlight lens',(0,0,0),[(0,0),(.134,0),(.13,.02),(0,.02)],m['cream']);lens.rotation_euler.x=math.pi/2;lens.location=(x,-.23,.64)
text('02',(-.21,-.061,.53),.32,m['cream'])
curve('Bent front bumper',[(-1.1,.15,.16),(-1.10,-.18,.16),(-.85,-.26,.16),(.85,-.26,.16),(1.10,-.18,.16),(1.10,.15,.16)],.055,m['iron'])
# A retained sliding door parks forward of its clear opening.
for y in [1.58,2.58]:box('Entry thick jamb',(1.15,y,1.23),(.20,.12,2.05),m['iron'],.025)
box('Entry threshold',(1.22,2.08,.22),(.34,.94,.12),m['iron'],.025)
box('Entry step',(1.47,2.08,-.03),(.54,1.08,.12),m['iron'],.035)
box('Sliding door lower panel',(1.30,1.02,.68),(.095,.94,.89),m['teal'],.045)
for y in [.54,1.50]:box('Sliding door stile',(1.30,y,1.28),(.095,.08,1.99),m['cream'],.02)
box('Sliding door top rail',(1.30,1.02,2.24),(.095,1.0,.10),m['cream'],.02)
box('Sliding door center rail',(1.30,1.02,1.12),(.095,1.0,.10),m['cream'],.02)
curve('Visible sliding upper track',[(1.31,.45,2.36),(1.31,2.64,2.36)],.035,m['iron'])
curve('Entry grab handle',[(1.38,1.43,1.15),(1.43,1.43,1.19),(1.43,1.43,1.55),(1.38,1.43,1.59)],.021,m['cream'])
# Repair plate, localized chips, fasteners and personal marks around entry.
box('Bolted repair patch',(1.218,2.99,.62),(.025,.61,.40),m['iron'],.015)
for y in [2.73,3.25]:
    for z in [.46,.78]:
        bolt=lathe('Patch bolt',(0,0,0),[(0,0),(.024,0),(.024,.014),(0,.014)],m['cream'],6);bolt.rotation_euler.y=math.pi/2;bolt.location=(1.24,y,z)
side_text('PATCH  07',(1.25,2.78,.60),.055,m['cream'])
for i in range(50):
    y=random.choice([.20,4.85])+random.uniform(-.10,.10);z=random.uniform(.25,.92)
    ob=box('Localized lower paint loss',(1.213,y,z),(.003,random.uniform(.012,.055),random.uniform(.008,.025)),rust);ob.rotation_euler.x=random.uniform(-.4,.4)
for i,(body,color) in enumerate([('NOISE',(.65,.58,.39)),('DIY',(.44,.11,.15)),('02',(.25,.35,.32)),('LATE',(.58,.49,.23))]):
    mm=material('Faded sticker %d'%i,color,.82);yy=2.63+i*.07;zz=1.15+i*.14
    box('Door surround sticker',(1.224,yy,zz),(.008,.17,.11),mm,.003);side_text(body,(1.235,yy-.073,zz-.018),.033,m['cream'])
group(before,'02_Shell')

# Actual glazing, thin gaskets and frames with restrained corner radii.
before=checkpoint()
for side in [-1.15,1.15]:
    spans=[(.19,1.34),(1.53,2.53),(2.73,3.73),(3.93,4.91)] if side<0 else [(.19,1.43),(2.73,3.73),(3.93,4.91)]
    for ya,yb in spans:
        box('Side glass pane',(side,(ya+yb)/2,1.67),(.008,yb-ya,1.03),m['glass'])
        rounded_loop('Side rubber channel',(side*1.005,(ya+yb)/2,1.67),yb-ya,1.08,.075,.021,rubber,'side')
        rounded_loop('Side enamel frame',(side*1.012,(ya+yb)/2,1.67),yb-ya+.055,1.13,.09,.024,m['cream'],'side')
for yy in [-.015,5.105]:
    for xa,xb in [(-1.02,-.07),(.07,1.02)]:
        box('Windscreen',((xa+xb)/2,yy,1.68),(xb-xa,.008,1.05),m['glass'])
        rounded_loop('Windscreen gasket',((xa+xb)/2,yy-.012,1.68),xb-xa,1.08,.08,.023,rubber)
        rounded_loop('Windscreen metal rim',((xa+xb)/2,yy-.020,1.68),xb-xa+.05,1.13,.09,.024,m['cream'])
for x in [-.78,.78]:curve('Cab windscreen wiper',[(x,-.06,1.16),(x+.22,-.06,1.79)],.012,m['iron'])
box('Sliding door glass',(1.30,1.02,1.68),(.008,.81,.99),m['glass'])
group(before,'04_Glazing')

# Separate, removable barrel roof, insulated lining, curved ribs and roof equipment.
before=checkpoint()
profile=[(-1.27+i*2.54/48,2.31+.39*math.sqrt(max(0,1-((-1.27+i*2.54/48)/1.28)**2))) for i in range(49)]
verts=[(x,y,z) for y in [-.16,5.26] for x,z in profile]
roof=mesh('Curved zinc roof',verts,[(i,i+1,50+i,49+i) for i in range(48)],roofmat,True)
roof.data.materials.append(m['wood']);solid=roof.modifiers.new('Roof lining thickness','SOLIDIFY');solid.thickness=.065;solid.material_offset=1
for y in [-.10+i*.47 for i in range(12)]:
    curve('Roof standing seam',[(x,y,z+.02) for x,z in profile[::4]],.009,m['iron'])
for y in [.32,1.54,2.72,3.92,4.88]:
    curve('Exposed curved interior rib',[(x*.94,y,z-.095) for x,z in profile[::4]],.028,m['cream'])
for x in [-1.27,1.27]:curve('Roof edge gutter',[(x,-.12,2.35),(x,5.23,2.35)],.03,m['iron'])
for y in [-.12,5.22]:
    pv=[(x,y,z) for x,z in profile]+[(1.27,y,2.25),(-1.27,y,2.25)]
    mesh('Roof end curved fascia',pv,[tuple(range(len(pv)))],m['teal'])
lathe('Roof ventilation cowl',(.28,4.20,2.69),[(0,0),(.17,0),(.17,.18),(.24,.21),(.23,.25),(0,.25)],roofmat)
box('Roof repaired panel',(.50,3.23,2.665),(.48,.53,.025),m['iron'],.025)
group(before,'03_Removable_roof')

# Domestic layer, bed base and individually supported floorboards.
before=checkpoint()
for i in range(12):box('Interior floorboard',(-1.015+i*.185,2.55,.24),(.178,4.91,.045),m['wood'],.005)
box('Bed recessed toe space',(-.43,3.87,.39),(1.06,1.76,.25),m['iron'],.035)
box('Lift-up bed platform',(-.43,3.87,.53),(1.20,1.90,.16),m['wood'],.055)
box('Rounded mattress',(-.43,3.87,.69),(1.19,1.90,.22),m['linen'],.105)
box('Rear headboard',(-.43,4.94,1.03),(1.28,.09,1.08),m['wood'],.055)
box('Entry woven rug',(.48,2.0,.275),(.67,1.00,.018),m['linen'],.015)
for x in [-1.055,1.055]:
    curve('Former luggage rail',[(x,2.70,2.19),(x,4.92,2.19)],.021,m['cream'])
    curve('Timber hand-height trim',[(x,.22,1.02),(x,1.4,1.02)],.03,m['wood'])
group(before,'05_Interior')

# Sculpted cloth surfaces: smooth broad folds plus fine material weave, no fake cloth claim.
before=checkpoint()
def quilt_z(x,y):
    u=(x+1.045)/1.23;v=(y-2.90)/1.56
    sag=.12*(max(0,(.07-u)/.07)**2+max(0,(u-.93)/.07)**2)+.15*max(0,(.08-v)/.08)**2
    return .835+.018*math.sin(x*18+y*8)+.012*math.sin(y*21-x*7)+.025*math.exp(-((y-3.65)/.22)**2)*math.sin(x*8)-sag
nx,ny=42,54
vv=[(-1.045+i*1.23/nx,2.90+j*1.56/ny,quilt_z(-1.045+i*1.23/nx,2.90+j*1.56/ny)) for j in range(ny+1) for i in range(nx+1)]
ff=[(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(ny) for i in range(nx)]
quilt=mesh('Patched quilt with drape',vv,ff,patchmats[0],True)
for mat in patchmats[1:]:quilt.data.materials.append(mat)
for face in quilt.data.polygons:
    j,i=divmod(face.index,nx);patch=(i//14,j//18)
    face.material_index={(0,0):1,(1,0):0,(2,0):2,(0,1):0,(1,1):2,(2,1):0,(0,2):2,(1,2):0,(2,2):3}.get(patch,0)
quilt.modifiers.new('Quilt thickness','SOLIDIFY').thickness=.025
for x in [-1.03,-.635,-.225,.17]:
    curve('Quilt stitched seam',[(x,2.92+j*1.51/40,quilt_z(x,2.92+j*1.51/40)+.009) for j in range(41)],.0017,m['linen'])
for y in [2.93,3.42,3.94,4.44]:
    curve('Quilt transverse stitch',[(-1.025+i*1.18/35,y,quilt_z(-1.025+i*1.18/35,y)+.009) for i in range(36)],.0017,m['linen'])
def pillow(name,center,radii,mat):
    def sp(v,e):return math.copysign(abs(v)**e,v)
    vv=[];nu,nv=64,28
    for j in range(nv+1):
        v=j*math.pi/nv
        for i in range(nu):
            u=i*math.tau/nu
            vv.append((center[0]+radii[0]*sp(math.cos(u),.6)*math.sin(v)**.6,center[1]+radii[1]*sp(math.sin(u),.6)*math.sin(v)**.6,center[2]+radii[2]*sp(math.cos(v),.7)+.007*math.sin(u*7)*math.sin(v)**2))
    ff=[(j*nu+i,j*nu+(i+1)%nu,(j+1)*nu+(i+1)%nu,(j+1)*nu+i) for j in range(nv) for i in range(nu)]
    return mesh(name,vv,ff,mat,True)
pillow('Compressed linen pillow',(-.43,4.57,.91),(.48,.23,.12),m['linen'])
pillow('Small mustard cushion',(-.77,4.27,.97),(.20,.20,.11),m['accent'])
# A folded wool throw adds a thicker, softer silhouette at the foot of the quilt.
nx2,ny2=40,18
vv2=[]
for j in range(ny2+1):
    v=j/ny2;y=3.03+v*.34
    for i in range(nx2+1):
        u=i/nx2;x=-1.02+u*1.18
        z=.89+.018*math.sin(x*12)+.045*math.sin(v*math.pi)**2-.07*max(0,(.08-u)/.08)**2-.07*max(0,(u-.92)/.08)**2
        vv2.append((x,y,z))
ff2=[(j*(nx2+1)+i,j*(nx2+1)+i+1,(j+1)*(nx2+1)+i+1,(j+1)*(nx2+1)+i) for j in range(ny2) for i in range(nx2)]
throw=mesh('Folded olive wool throw',vv2,ff2,curtainmat,True);throw.modifiers.new('Wool thickness','SOLIDIFY').thickness=.02
# Tied curtains occupy the rear ends of the side rails, leaving clear viewing bays.
for side in [-1.035,1.035]:
    nu,nv=20,36;vv=[]
    for j in range(nv+1):
        v=j/nv;z=2.17-v*1.15;width=.34-.19*math.exp(-((v-.57)/.16)**2)
        for i in range(nu+1):
            u=i/nu;vv.append((side+.022*math.sin(u*math.pi*10),4.79+(u-.5)*width,z+.014*math.sin(u*8)))
    ff=[(j*(nu+1)+i,j*(nu+1)+i+1,(j+1)*(nu+1)+i+1,(j+1)*(nu+1)+i) for j in range(nv) for i in range(nu)]
    ob=mesh('Tied olive curtain',vv,ff,curtainmat,True);ob.modifiers.new('Curtain fabric thickness','SOLIDIFY').thickness=.006
    curve('Curtain strap',[(side-.03,4.69,1.52),(side-.04,4.79,1.49),(side-.03,4.88,1.52)],.018,m['accent'])
group(before,'06_Textiles')

before=checkpoint();add_bedroom_props(m)
# Present the cab stool stowed beneath the desk; it can be pulled into the aisle.
for ob in set(bpy.data.objects)-before:
    if ob.name.startswith(('Tuckable stool','Stool splayed','Stool cross')):ob.location.y-=.40
group(before,'07_Props')

# Warm practical lighting and small, motivated colored accents.
before=checkpoint()
curve('Bedside lamp bent arm',[(-1.0,4.45,1.20),(-.93,4.45,1.50),(-.74,4.45,1.51)],.015,m['cream'])
lathe('Bedside lamp shade',(-.72,4.45,1.35),[(.16,0),(.15,.035),(.08,.18),(.07,.20)],m['cream'])
lathe('Bedside warm diffuser',(-.72,4.45,1.35),[(0,0),(.135,0)],m['amber'])
area_light('Bedside practical',(-.72,4.45,1.34),18,(1,.56,.25),.24,(-.3,3.8,.75))
area_light('Soft warm room bounce',(0,2.75,2.25),45,(1,.64,.34),1.5,(-.2,3.8,.5))
curve('Concealed rail reading strip',[(-1.035,2.85,2.17),(-1.035,4.5,2.17)],.009,m['amber'])
box('Neon bracket',(1.24,2.89,2.28),(.18,.62,.07),m['iron'],.015)
box('Neon dark backing',(1.32,2.89,2.26),(.045,.58,.23),m['iron'],.015)
side_text('HOME',(1.352,2.65,2.19),.14,pink)
curve('Sign supply cable',[(1.24,2.60,2.28),(1.24,2.67,2.10),(1.24,2.68,1.96)],.009,rubber)
box('Electrical service box',(1.25,2.68,1.88),(.085,.13,.17),m['iron'],.018)
box('Cyan step courtesy light',(1.52,2.08,-.06),(.40,.75,.014),cyan,.008)
if not a.neon_off:
    area_light('Magenta entrance spill',(1.54,2.88,2.23),12,(1,.04,.24),.5,(.3,2.45,1.0))
    area_light('Cyan step spill',(1.5,2.08,-.08),5,(.06,.65,.85),.5,(1.8,2.08,-.8))
group(before,'08_Lighting')

# One root moves the whole car while the studio stays independent.
asset_root=bpy.data.objects.new('LAST_STOP_ASSET_ROOT',None);scene.collection.objects.link(asset_root)
asset_root.empty_display_type='PLAIN_AXES'
for cname,col in collections.items():
    if cname!='09_Presentation':
        for ob in col.objects:ob.parent=asset_root
# Neutral presentation stage keeps focus on the standalone object, rather than a city.
before=checkpoint()
stage=material('Studio charcoal',(.028,.041,.055),.54)
box('Display slab',(0,2.55,-1.06),(3.4,6.65,.18),stage,.10)
cross=[(-100,-1.18),(8,-1.18)]+[(8+4*math.cos(-math.pi/2+i*math.pi/2/40),2.82+4*math.sin(-math.pi/2+i*math.pi/2/40)) for i in range(1,41)]+[(12,100)]
cycverts=[(x,y,z) for x in [-100,100] for y,z in cross]
ncross=len(cross)
mesh('Curved studio backdrop',cycverts,[(i,i+1,ncross+i+1,ncross+i) for i in range(ncross-1)],stage,True)
world=bpy.data.worlds.new('Muted blue studio');world.use_nodes=True;scene.world=world
world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.17,.26,1);world.node_tree.nodes['Background'].inputs[1].default_value=.32
area_light('Large cool key',(3,-3,7),850,(.74,.86,1),5,(0,2.5,1))
area_light('Blue side fill',(-4,2.5,4),450,(.33,.54,1),4,(0,2.5,1))
area_light('Soft roof rim',(1,7.5,6),700,(.74,.85,1),3,(0,2.5,1))
bpy.ops.object.camera_add();camera=bpy.context.object;camera.name='Hero camera';scene.camera=camera
cameras={
 'hero':((8,-8,4.4),(0,2.45,1.05),52),
 'entry':((1.85,1.65,1.60),(-.35,3.90,1.03),25),
 'cutaway':((5.5,-2.5,10),(0,2.55,.65),48),
}
for view,(loc,target,lens) in cameras.items():
    if view=='hero':cam=camera
    else:
        data=bpy.data.cameras.new(view+' lens');cam=bpy.data.objects.new(view.title()+' camera',data);scene.collection.objects.link(cam)
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    if view=='cutaway':cam.data.type='ORTHO';cam.data.ortho_scale=7.4
    cameras[view]=(cam,None,None)
group(before,'09_Presentation')
scene.render.engine='CYCLES';scene.cycles.samples=a.samples;scene.cycles.use_denoising=False
scene.cycles.max_bounces=10;scene.cycles.transmission_bounces=6
scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.render.resolution_percentage=a.scale
scene.render.image_settings.file_format='PNG';scene.render.threads_mode='FIXED';scene.render.threads=5
scene.view_settings.view_transform='AgX'
scene.camera=camera;scene.render.filepath=str(ROOT/'renders/bedroom-hero.png')
(ROOT/'scenes').mkdir(exist_ok=True);(ROOT/'renders').mkdir(exist_ok=True)
if a.scale==100:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scenes/funicular-bedroom.blend'),compress=True)
for view in (cameras if a.view=='all' else [a.view]):
    scene.camera=cameras[view][0]
    collections['03_Removable_roof'].hide_render=view=='cutaway'
    scene.render.filepath=str(ROOT/'renders'/('bedroom-'+view+('-warm' if a.neon_off else '')+'.png'))
    bpy.ops.render.render(write_still=True)
