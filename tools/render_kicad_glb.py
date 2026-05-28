import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / "pcb" / "renders" / "pitalk_pcb_3d.glb"
OUT = ROOT / "pcb" / "renders" / "pitalk_pcb_kicad_3d_render.png"


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

bpy.ops.import_scene.gltf(filepath=str(GLB))

objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
for obj in objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = objects[0] if objects else None

min_corner = Vector((float("inf"), float("inf"), float("inf")))
max_corner = Vector((float("-inf"), float("-inf"), float("-inf")))
for obj in objects:
    for corner in obj.bound_box:
        world = obj.matrix_world @ Vector(corner)
        min_corner.x = min(min_corner.x, world.x)
        min_corner.y = min(min_corner.y, world.y)
        min_corner.z = min(min_corner.z, world.z)
        max_corner.x = max(max_corner.x, world.x)
        max_corner.y = max(max_corner.y, world.y)
        max_corner.z = max(max_corner.z, world.z)

center = (min_corner + max_corner) / 2
extent = max(max_corner.x - min_corner.x, max_corner.y - min_corner.y, max_corner.z - min_corner.z)

empty = bpy.data.objects.new("Board Center", None)
bpy.context.collection.objects.link(empty)
empty.location = center

camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
bpy.context.collection.objects.link(camera)
bpy.context.scene.camera = camera
camera.location = center + Vector((extent * 0.8, -extent * 1.0, extent * 1.0))
camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = extent * 1.55
camera.data.dof.use_dof = False

sun = bpy.data.objects.new("Key Sun", bpy.data.lights.new("Key Sun", "SUN"))
bpy.context.collection.objects.link(sun)
sun.location = center + Vector((0, -extent, extent * 2))
sun.rotation_euler = (math.radians(45), 0, math.radians(35))
sun.data.energy = 0.8

area = bpy.data.objects.new("Softbox", bpy.data.lights.new("Softbox", "AREA"))
bpy.context.collection.objects.link(area)
area.location = center + Vector((extent * 0.2, -extent * 0.4, extent * 1.8))
area.data.energy = 120
area.data.size = extent

bpy.context.scene.render.engine = "BLENDER_WORKBENCH"
bpy.context.scene.display.shading.light = "STUDIO"
bpy.context.scene.display.shading.color_type = "MATERIAL"
bpy.context.scene.display.shading.show_cavity = True
bpy.context.scene.view_settings.view_transform = "Standard"
bpy.context.scene.view_settings.look = "Medium High Contrast"
bpy.context.scene.view_settings.exposure = 0
bpy.context.scene.view_settings.gamma = 1
bpy.context.scene.render.resolution_x = 1800
bpy.context.scene.render.resolution_y = 1300
bpy.context.scene.render.film_transparent = False
bpy.context.scene.world.color = (0.78, 0.78, 0.78)

bpy.context.scene.render.filepath = str(OUT)
bpy.ops.render.render(write_still=True)
