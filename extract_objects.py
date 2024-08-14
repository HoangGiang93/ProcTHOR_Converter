#!/usr/bin/env python3.11

import bpy
import re
import os
from mathutils import Vector, Euler
from math import radians

source_dir = os.path.dirname(os.path.realpath(__file__))

grp_meshes_dir = os.path.join(source_dir, 'raw_grp_meshes')
grp_objects_dir = os.path.join(source_dir, 'grp_objects')

single_meshes_dir = os.path.join(source_dir, 'raw_single_meshes')
single_objects_dir = os.path.join(source_dir, 'single_objects')

ignore_list = ['stretch_robot_camera_brackets_grp.fbx',
               'calibration_room_grp.fbx']
ignore_name = ['FloorPlan']

ignore_meshes = [
    'Remotebody_2',
    'Remotebody_3',
    'Remotebody_4',
    'Remotebuttons_2',
    'Remotebuttons_3',
    'Toilet_1_Done_0',
    'Toilet_2_1',
    'Toilet_2_2',
    'Toilet_2_3',
]

scale_objects = {
    "Toilet_1_Done": [2.424, 2.424, 2.214],
    "Toilet_2": [5.64, 5.64, 5.15],
    "CountertopL": [-1.0, 1.0, 1.0]
}

rotate_objects = {
    "Toilet_1_Done": Euler((0, 0, radians(180)))
}

translate_objects = {
    "Toilet_1_Done": [-0.2, 0.0, 0.0],
}

def snake_to_camel(snake_str):
     # Split the string by underscores, but keep numbers separated
    components = re.split(r'(_\d+_)|(_\d+)|(_\d+)|_', snake_str)
    
    # Filter out None or empty strings that might result from the split
    components = [comp for comp in components if comp]
    
    # Capitalize the first letter of each component except those that are purely numeric
    camel_str = ''.join(comp.title() if not comp.isdigit() else comp for comp in components)

    camel_str = re.sub(r'(\d+)', r'_\1_', camel_str)

    camel_str = camel_str.strip('_').replace('.', '_').replace(' ', '_').replace('__', '_')
    
    return camel_str

def select_object_with_children(obj, reset_origin=True):
    # Select the parent object
    obj.select_set(True)

    # Set the origin to geometry
    if reset_origin:
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # Recursively select all children
    for child in obj.children:
        select_object_with_children(child)

def extract_grp_object(fbx_file_path):
    data = bpy.data

    for armature in data.armatures:
        data.armatures.remove(armature)
    for mesh in data.meshes:
        data.meshes.remove(mesh)
    for object in data.objects:
        data.objects.remove(object)
    for material in data.materials:
        data.materials.remove(material)
    for camera in data.cameras:
        data.cameras.remove(camera)
    for light in data.lights:
        data.lights.remove(light)
    for image in data.images:
        data.images.remove(image)

    bpy.ops.import_scene.fbx(filepath=fbx_file_path)

    # Deselect all objects first
    bpy.ops.object.select_all(action='DESELECT')

    # Select all objects in the scene
    bpy.ops.object.select_all(action='SELECT')

    # Apply all transformations (location, rotation, scale)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    while True:
        # Iterate over all objects in the scene
        for obj in bpy.context.scene.objects:
            # Check if the object is a top-level object by verifying it has no parent
            if obj.type != 'MESH' and obj.parent is None:
                # Delete the object
                bpy.data.objects.remove(obj, do_unlink=True)
        if not any(obj.type != 'MESH' and obj.parent is None for obj in bpy.context.scene.objects):
            break

    # Iterate over all objects in the scene
    for obj in bpy.context.scene.objects:
        # Rename the object
        obj.name = snake_to_camel(obj.name)
        obj.data.name = f"SM_{obj.name}"
        
        # Iterate over all materials assigned to the mesh
        for index, material in enumerate(obj.data.materials):
            if material:  # Check if the material slot is not empty
                # Rename the material
                material.name = f"M_{obj.name}_{index}"

    # Iterate over all objects in the scene
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.parent is None and 'Slice' not in obj.name:
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            
            select_object_with_children(obj)

            # Move the origin to zeros
            obj.location[0] = 0
            obj.location[1] = 0
            obj.location[2] = 0

            for obj_name, scale in scale_objects.items():
                if obj_name in obj.name:
                    obj.scale[0] *= scale[0]
                    obj.scale[1] *= scale[1]
                    obj.scale[2] *= scale[2]

                    if scale[0] * scale[1] * scale[2] < 0:
                        # Flip all faces
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.mesh.flip_normals()
                        bpy.ops.object.mode_set(mode='OBJECT')
                    break
            
            # Set the object as the active object
            bpy.context.view_layer.objects.active = obj
            
            # Apply all transformations (location, rotation, scale)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            
            # Define the output file path
            obj_dir_path = os.path.join(grp_objects_dir, obj.name)
            if not os.path.exists(obj_dir_path):
                os.makedirs(obj_dir_path)
            obj_file_path = os.path.join(obj_dir_path, f"{obj.name}.obj")
            
            # Export the selected object to an .obj file
            bpy.ops.wm.obj_export(filepath=obj_file_path, export_selected_objects=True, forward_axis='Y', up_axis='Z')

            obj_file_path = os.path.join(obj_dir_path, f"{obj.name}.stl")
            
            # Export the selected object to an .stl file
            bpy.ops.wm.stl_export(filepath=obj_file_path, export_selected_objects=True, forward_axis='Y', up_axis='Z')

def extract_single_object(fbx_file_path):
    data = bpy.data

    for armature in data.armatures:
        data.armatures.remove(armature)
    for mesh in data.meshes:
        data.meshes.remove(mesh)
    for object in data.objects:
        data.objects.remove(object)
    for material in data.materials:
        data.materials.remove(material)
    for camera in data.cameras:
        data.cameras.remove(camera)
    for light in data.lights:
        data.lights.remove(light)
    for image in data.images:
        data.images.remove(image)

    bpy.ops.import_scene.fbx(filepath=fbx_file_path)

    # Deselect all objects first
    bpy.ops.object.select_all(action='DESELECT')

    # Select all objects in the scene
    bpy.ops.object.select_all(action='SELECT')

    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)

    while True:
        # Iterate over all objects in the scene
        for obj in bpy.context.scene.objects:
            # Check if the object is a top-level object by verifying it has no parent
            if obj.type != 'MESH':
                # Delete the object
                bpy.data.objects.remove(obj, do_unlink=True)
        if not any(obj.type != 'MESH' for obj in bpy.context.scene.objects):
            break

    # Iterate over all objects in the scene
    for obj in bpy.context.scene.objects:
        # Rename the object
        obj.name = snake_to_camel(obj.name)
        obj.data.name = f"SM_{obj.name}"
        
        # Iterate over all materials assigned to the mesh
        for index, material in enumerate(obj.data.materials):
            if material:  # Check if the material slot is not empty
                # Rename the material
                material.name = f"M_{obj.name}_{index}"

    # Define the output file path
    obj_file_name = os.path.basename(fbx_file_path).split('.')[0]
    obj_file_name = snake_to_camel(obj_file_name)
    obj_dir_path = os.path.join(single_objects_dir, obj_file_name)
    if not os.path.exists(obj_dir_path):
        os.makedirs(obj_dir_path)

    # Iterate over all objects in the scene
    for i, obj in enumerate(bpy.context.scene.objects):
        if obj.type == 'MESH' and obj.parent is None and obj.name not in ignore_meshes:
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            
            select_object_with_children(obj, True)

            # Move the origin to zeros
            obj.location[0] = 0
            obj.location[1] = 0
            obj.location[2] = 0

            # Get the bounding box of the mesh object in world coordinates
            bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            
            # Find the minimum and maximum coordinates in world space
            min_x = min(corner.x for corner in bbox_corners)
            max_x = max(corner.x for corner in bbox_corners)
            min_y = min(corner.y for corner in bbox_corners)
            max_y = max(corner.y for corner in bbox_corners)
            min_z = min(corner.z for corner in bbox_corners)
            max_z = max(corner.z for corner in bbox_corners)
            
            # Calculate dimensions
            width = max_x - min_x
            height = max_y - min_y
            depth = max_z - min_z
            
            # Check if any dimension exceeds 1 meter
            if width > 1 or height > 1 or depth > 1:
                obj.scale[0] *= 0.1
                obj.scale[1] *= 0.1
                obj.scale[2] *= 0.1

            if obj_file_name in scale_objects:
                obj.scale[0] *= scale_objects[obj_file_name][0]
                obj.scale[1] *= scale_objects[obj_file_name][1]
                obj.scale[2] *= scale_objects[obj_file_name][2]

                if scale_objects[obj_file_name][0] * scale_objects[obj_file_name][1] * scale_objects[obj_file_name][2] < 0:
                    # Flip all faces
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.flip_normals()
                    bpy.ops.object.mode_set(mode='OBJECT')

            if obj_file_name in rotate_objects:
                obj.rotation_mode = "XYZ"
                obj.rotation_euler.rotate(rotate_objects[obj_file_name])
                
            if obj_file_name in translate_objects:
                obj.location[0] += translate_objects[obj_file_name][0]
                obj.location[1] += translate_objects[obj_file_name][1]
                obj.location[2] += translate_objects[obj_file_name][2]
            
            # Set the object as the active object
            bpy.context.view_layer.objects.active = obj
            
            # Apply all transformations (location, rotation, scale)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

            if 'Sphere' in obj.name or 'Cube' in obj.name or 'Cylinder' in obj.name:
                obj_export_file_name = f"{obj_file_name}_{i}"
            else:
                obj_export_file_name = obj.name

            if obj_export_file_name in ignore_meshes:
                continue

            obj_file_path = os.path.join(obj_dir_path, f"{obj_export_file_name}.stl")
            
            # Export the selected object to an .stl file
            bpy.ops.wm.stl_export(filepath=obj_file_path, export_selected_objects=True, forward_axis='Y', up_axis='Z')

if __name__=="__main__":
    for root, dirs, files in os.walk(grp_meshes_dir):
        for fbx_file in files:
            if fbx_file.endswith('.fbx') and fbx_file not in ignore_list:
                fbx_file_path = os.path.join(root, fbx_file)
                print(f"Extracting objects from {fbx_file_path}")
                extract_grp_object(fbx_file_path)

    for root, dirs, files in os.walk(single_meshes_dir):
        for fbx_file in files:
            if fbx_file.endswith('.fbx') and fbx_file not in ignore_list and not any(name in fbx_file for name in ignore_name):
                fbx_file_path = os.path.join(root, fbx_file)
                print(f"Extracting object from {fbx_file_path}")
                extract_single_object(fbx_file_path)