import bpy
import random
import math

# Function to ensure an object is in the active view layer
def ensure_in_view_layer(obj):
    if obj.name not in bpy.context.view_layer.objects:
        bpy.context.scene.collection.objects.link(obj)
    obj.hide_viewport = False
    obj.hide_render = False

# Function to point the camera at an object
def point_camera_at_object(camera, target):
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

# Function to set up material for color animation
def setup_material_for_color_animation(obj):
    if not obj.data.materials:
        mat = bpy.data.materials.new(name="ColorAnimMaterial")
        obj.data.materials.append(mat)
    else:
        mat = obj.data.materials[0]
    
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear existing nodes
    nodes.clear()
    
    # Create new nodes
    diffuse_node = nodes.new(type='ShaderNodeBsdfDiffuse')
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Link nodes
    links.new(diffuse_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    return diffuse_node

# Select the molecular object by name
molecule_name = "NewMolecule.002"
molecule_obj = bpy.data.objects.get(molecule_name)
if not molecule_obj:
    raise ValueError(f"Object named '{molecule_name}' not found in the scene.")
ensure_in_view_layer(molecule_obj)
bpy.context.view_layer.objects.active = molecule_obj
molecule_obj.select_set(True)

# Set up material for color animation
color_node = setup_material_for_color_animation(molecule_obj)

# Set the total number of frames for the animation
total_frames = 250
bpy.context.scene.frame_end = total_frames

# Function to add a glow effect to specific atoms
def add_glow_effect(obj, frame, strength=5.0):
    mat_name = f"GlowMaterial_{obj.name}"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        obj.data.materials.append(mat)
    
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear existing nodes
    nodes.clear()
    
    # Create emission node
    emission_node = nodes.new(type='ShaderNodeEmission')
    emission_node.inputs['Strength'].default_value = strength
    
    # Create output node
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Link nodes
    links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])
    
    # Keyframe the emission strength
    emission_node.inputs['Strength'].keyframe_insert(data_path="default_value", frame=frame)

# Insert keyframes for complex transformations
for frame in range(0, total_frames + 1, 10):
    bpy.context.scene.frame_set(frame)
    
    # Rotation animation
    molecule_obj.rotation_euler = (frame * 0.05, frame * 0.03, frame * 0.07)
    molecule_obj.keyframe_insert(data_path="rotation_euler", index=-1)
    
    # Translation animation (oscillating movement)
    molecule_obj.location = (2 * random.uniform(-1, 1), 2 * random.uniform(-1, 1), 2 * random.uniform(-1, 1))
    molecule_obj.keyframe_insert(data_path="location", index=-1)
    
    # Color change animation
    color = (random.random(), random.random(), random.random(), 1)
    color_node.inputs['Color'].default_value = color
    color_node.inputs['Color'].keyframe_insert(data_path="default_value", frame=frame)
    
    # Add glow effect to a random atom if there are any children
    if molecule_obj.children:
        random_atom = random.choice(molecule_obj.children)
        add_glow_effect(random_atom, frame, strength=10.0)

# Dynamically find or create the camera object
camera = bpy.data.objects.get('Camera')
if not camera:
    bpy.ops.object.camera_add(location=(10, 10, 10))
    camera = bpy.context.active_object
ensure_in_view_layer(camera)

# Point the camera at the molecule
point_camera_at_object(camera, molecule_obj)

# Animate the camera
for frame in range(0, total_frames + 1, 25):
    bpy.context.scene.frame_set(frame)
    
    # Move the camera in a circular path around the molecule
    angle = frame * 0.05
    radius = 15
    camera.location = (
        radius * math.cos(angle),
        radius * math.sin(angle),
        10 + 5 * math.sin(angle * 0.5)
    )
    camera.keyframe_insert(data_path="location", index=-1)

bpy.context.view_layer.objects.active = camera
camera.select_set(True)

# Set up lighting
light = bpy.data.objects.get('Light')
if not light:
    bpy.ops.object.light_add(type='POINT', location=(5, 5, 5))
    light = bpy.context.active_object
ensure_in_view_layer(light)
light.data.energy = 1000
light.keyframe_insert(data_path="location", frame=0)
light.data.keyframe_insert(data_path="energy", frame=0)

for frame in range(0, total_frames + 1, 50):
    bpy.context.scene.frame_set(frame)
    light.location = (5 + frame * 0.05, 5 - frame * 0.05, 5 + frame * 0.05)
    light.data.energy = 1000 + frame * 10
    light.keyframe_insert(data_path="location", index=-1)
    light.data.keyframe_insert(data_path="energy", frame=frame)

# Play the animation
bpy.ops.screen.animation_play()