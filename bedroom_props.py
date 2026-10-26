"""Furniture and personal fittings for the standalone LAST STOP sleeper car.

No scene loading or rendering occurs at import. Coordinates are metres in the
car's local space: front Y=0, rear Y=5.1 and finished floor Z=.2.
"""
import math

import bpy

from blender_shapes import box, curve, lathe, material, text


def _desk_top(mat):
    # Follow the windscreen instead of placing a rectangular office desk inside.
    outline = [(-.95,.80),(-.95,.45),(-.79,.34),(-.38,.28),
               (.12,.29),(.54,.37),(.80,.51),(.80,.84)]
    count = len(outline)
    vertices = [(x,y,z) for z in [.88,.95] for x,y in outline]
    faces = [tuple(reversed(range(count))), tuple(range(count,2*count))]
    faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    mesh = bpy.data.meshes.new('Fitted curved cab desktop mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new('Fitted curved cab desktop', mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Worn desktop edges', 'BEVEL')
    bevel.width = .018
    bevel.segments = 3
    obj.modifiers.new('Desktop normals', 'WEIGHTED_NORMAL')
    return obj


def _cab_gauge(x, y, z, cream, iron, accent):
    bezel = lathe('Retained cab gauge bezel',(x,y,z),
                  [(0,0),(.053,0),(.059,.012),(.057,.026),(0,.026)],iron,32)
    bezel.rotation_euler.x = -math.pi/2  # instruments face the driver at +Y
    dial = lathe('Faded cab gauge face',(x,y+.028,z),[(0,0),(.047,0)],cream,32)
    dial.rotation_euler.x = -math.pi/2
    for i in range(7):
        a = math.radians(-55+i*48)
        curve('Gauge tick',[(x+.037*math.cos(a),y+.031,z+.037*math.sin(a)),
                            (x+.043*math.cos(a),y+.031,z+.043*math.sin(a))],.0014,iron)
    curve('Gauge red needle',[(x-.008,y+.033,z-.008),
                              (x+.028,y+.033,z+.025)],.002,accent)


def _mug(name, x, y, z, mat):
    lathe(name,(x,y,z),[(0,0),(.045,0),(.052,.014),(.058,.12),
                      (.050,.13),(.043,.12),(.041,.022),(0,.022)],mat,28)
    curve(name+' handle',[(x+.047,y,z+.105),(x+.091,y,z+.10),
                         (x+.091,y,z+.035),(x+.047,y,z+.032)],.009,mat)


def add_bedroom_props(materials):
    """Create furniture/fittings in the active scene and return created objects.

    The parent generator supplies shell, bedding, curtains and lighting. This
    function keeps the mid-right entrance and the aisle beside the bed clear.
    """
    before = set(bpy.data.objects)
    wood = materials['wood']; teal = materials['teal']
    iron = materials['iron']; cream = materials['cream']
    fabric = materials['fabric']; linen = materials['linen']
    accent = materials['accent']; amber = materials['amber']
    dark = material('Personal prop black rubber',(.018,.024,.021),.72)
    paper = material('Personal notebook paper',(.62,.55,.37),.88)
    coffee = material('Cold bedside tea',(.035,.018,.008),.16)

    # Fitted desk with visible brackets; a compact stool disappears underneath.
    _desk_top(wood)
    for x in [-.78,.65]:
        curve('Cab desk wall bracket',[(x,.36,.46),(x,.36,.87),(x,.74,.87)],.025,iron)
    box('Cab control plinth',(.50,.42,1.07),(.49,.15,.24),teal,.025)
    for x in [.38,.63]:
        _cab_gauge(x,.508,1.10,cream,iron,accent)
    curve('Retained control lever',[(-.62,.44,.96),(-.62,.44,1.08),(-.55,.50,1.22)],.017,iron)
    lathe('Worn control lever grip',(-.55,.50,1.21),
          [(0,0),(.026,0),(.039,.025),(.035,.07),(.018,.085),(0,.085)],dark,24)
    lathe('Lever mounting flange',(-.62,.44,.95),[(0,0),(.075,0),(.075,.018),(0,.018)],iron,24)
    # Flat engraved switch labels face upward, readable from inside the cab.
    for x,label in [(-.08,'ROOM'),(.13,'SIGN')]:
        box('Repurposed switch label '+label,(x,.58,.965),(.17,.12,.018),cream,.009)
        txt=text(label,(x+.055,.615,.977),.028,iron)
        txt.rotation_euler=(0,0,math.pi)
        curve('Room switch toggle '+label,[(x,.54,.976),(x-.012,.54,1.015)],.006,iron)
        lathe('Switch rubber boot '+label,(x,.54,.978),[(0,0),(.014,0),(.014,.012),(0,.012)],dark,16)
    lathe('Tuckable stool cushion',(-.25,.99,.535),
          [(0,0),(.19,0),(.22,.03),(.22,.075),(.19,.095),(0,.095)],fabric,32)
    for dx,dy in [(-.13,-.12),(.13,-.12),(-.13,.12),(.13,.12)]:
        curve('Stool splayed leg',[(-.25+dx*1.20,.99+dy*1.20,.20),
                                  (-.25+dx,.99+dy,.555)],.024,iron)
    curve('Stool cross brace',[(-.41,.99,.34),(-.09,.99,.34)],.014,iron)
    # Notebook and repaired portable audio player, kept low enough for the view.
    box('Closed notebook',(-.29,.59,.982),(.28,.19,.028),fabric,.009)
    box('Notebook page block',(-.29,.586,.993),(.255,.166,.013),paper,.003)
    curve('Pencil on notebook',[(-.39,.57,1.008),(-.19,.63,1.008)],.004,wood)
    box('Battered portable audio player',(-.67,.67,1.024),(.25,.12,.12),teal,.018)
    box('Audio player dark face',(-.67,.738,1.024),(.218,.014,.084),dark,.009)
    # Speaker rings, rather than a flat black rectangular face.
    for x in [-.74,-.60]:
        ring = lathe('Audio player speaker',(x,.748,1.027),
                     [(0,0),(.029,0),(.033,.004),(.027,.009),(0,.009)],iron,24)
        ring.rotation_euler.x=-math.pi/2
    curve('Clipped desk power cable',[(-.78,.66,.95),(-.92,.69,.89),
                                     (-.97,.95,.58),(-.98,1.10,.35)],.009,dark)
    for y,z in [(.93,.63),(1.08,.39)]:
        box('Desk cable retaining clip',(-.978,y,z),(.025,.04,.04),iron,.006)

    # Shallow left cabinet at the entrance. Handles face inward along +X.
    box('Mid-left shallow storage',(-.88,1.86,.59),(.34,1.08,.76),wood,.024)
    for y in [1.60,2.12]:
        box('Cabinet inset door',(-.698,y,.59),(.035,.48,.65),teal,.015)
        curve('Cabinet pull', [(-.666,y-.055,.69),(-.645,y-.055,.69),
                               (-.645,y+.055,.69),(-.666,y+.055,.69)],.009,iron)
    box('Cabinet rounded top',(-.88,1.86,.993),(.39,1.15,.07),wood,.026)
    # A neatly folded cloth has seams and rounded layers, not a hanging garment
    # volume that would compete with the circulation path.
    for i in range(3):
        cloth=box('Folded worn cloth',(-.89,2.13,1.045+i*.021),(.25,.24,.023),linen,.011)
        cloth.rotation_euler.z=math.radians(-5+i*3)
    curve('Folded cloth visible seam',[(-.995,2.02,1.095),(-.89,2.025,1.095),(-.79,2.035,1.095)],.0025,fabric)
    for y in [1.51,1.89,2.25]:
        box('Coat hook wall mounting',(-1.055,y,1.52),(.032,.065,.11),iron,.009)
        curve('Retained transit coat hook',[(-1.03,y,1.54),(-.95,y,1.51),
                                            (-.95,y,1.47),(-.99,y,1.46)],.012,iron)
    # A strap loop hints at a hung bag while preserving the clear door landing.
    curve('Repurposed fabric hanging strap',[(-1.015,1.89,1.51),(-.94,1.85,1.35),
                                              (-1.005,1.89,1.18)],.016,fabric)

    # Bedside pocket stays close to the left lining, above the bed edge.
    box('Bedside recessed pocket back',(-1.067,4.45,1.26),(.025,.43,.29),teal,.009)
    box('Bedside timber niche shelf',(-.973,4.45,1.12),(.22,.46,.045),wood,.016)
    for y in [4.23,4.67]:
        box('Bedside pocket end',(-.99,y,1.245),(.18,.025,.23),wood,.009)
    book=box('Bedside paperback',(-.981,4.51,1.166),(.14,.20,.032),accent,.008)
    book.rotation_euler.z=math.radians(7)
    box('Paperback page edges',(-.981,4.508,1.178),(.125,.18,.013),paper,.002)
    _mug('Bedside enamel mug',-.951,4.31,1.146,cream)
    lathe('Tea surface',(-.951,4.31,1.25),[(0,0),(.044,0)],coffee,24)

    # Slim opposite ledge: deliberately avoid drawers opening across the aisle.
    box('Rear-right shallow ledge',(.95,3.84,1.025),(.20,1.48,.05),wood,.016)
    for y in [3.23,4.44]:
        curve('Right ledge bracket',[(1.045,y,.83),(1.045,y,1.0),(.87,y,1.0)],.017,iron)
    # Two small leaning zines with readable silhouettes.
    for y,h in [(3.36,.24),(3.48,.19)]:
        zine=box('Personal zine on ledge',(.997,y,1.06+h/2),(.028,.13,h),fabric if h>.2 else accent,.004)
        zine.rotation_euler.y=math.radians(-7)
    # A restrained cassette case and pencil cup live farther from the entrance.
    box('Cassette case on ledge',(.945,4.12,1.069),(.14,.11,.028),cream,.006)
    lathe('Pencil cup',(.931,4.40,1.052),[(0,0),(.04,0),(.045,.12),(.035,.13),(.03,.02),(0,.02)],teal,24)
    for dx,dy in [(-.01,0),(.014,.007),(0,-.011)]:
        curve('Ledge pencil',[(.931+dx,4.40+dy,1.09),(.94+dx,4.40+dy,1.26)],.003,wood)

    # The destination box remains outside, visible in the intact exterior view.
    box('LAST STOP destination housing',(0,-.105,2.235),(1.20,.16,.23),iron,.035)
    box('Destination warm face',(0,-.194,2.235),(1.08,.015,.155),amber,.017)
    sign=text('LAST STOP',(-.46,-.207,2.186),.133,iron)
    sign.name='LAST STOP destination lettering'
    for x in [-.52,.52]:
        curve('Destination mounting bracket',[(x,-.04,2.20),(x,.03,2.20),(x,.03,2.32)],.018,iron)
    curve('Destination supply cable',[(.57,-.07,2.20),(.72,.03,2.24),(.91,.13,2.24)],.008,dark)

    created=[obj for obj in bpy.data.objects if obj not in before]
    return created
