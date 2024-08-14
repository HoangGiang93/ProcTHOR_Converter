#!/usr/bin/env python3

import os
import shutil

source_dir = os.path.dirname(os.path.realpath(__file__))

source_folder = os.path.join(source_dir, 'ai2thor/unity/Assets')
destination_grp_folder = os.path.join(source_dir, 'raw_grp_meshes')
destination_single_folder = os.path.join(source_dir, 'raw_single_meshes')

def copy_fbx_files():
    # Ensure the destination folder exists
    if not os.path.exists(destination_grp_folder):
        os.makedirs(destination_grp_folder)

    if not os.path.exists(destination_single_folder):
        os.makedirs(destination_single_folder)

    # Walk through the source folder and its subdirectories
    for root, dirs, files in os.walk(source_folder):
        for fbx_file in files:
            if fbx_file.endswith('.fbx') and not fbx_file.endswith('shards_grp.fbx'):
                # Construct full file paths
                source_fbx_file = os.path.join(root, fbx_file)
                destination_dir_name = fbx_file.split('.')[0]
                if fbx_file.endswith('grp.fbx'):
                    destination_dir = os.path.join(destination_grp_folder, destination_dir_name)
                else:
                    destination_dir = os.path.join(destination_single_folder, destination_dir_name)
                if not os.path.exists(destination_dir):
                    os.makedirs(destination_dir)
                destination_fbx_file = os.path.join(destination_dir, fbx_file)
                
                # Copy the file to the destination folder
                shutil.copy2(source_fbx_file, destination_fbx_file)
                print(f'Copied: {source_fbx_file} to {destination_fbx_file}')

                for png_file in files:
                    if png_file.endswith('.png'):
                        # Construct full file paths
                        source_png_file = os.path.join(root, png_file)
                        destination_png_file = os.path.join(destination_dir, png_file)

                        # Copy the file to the destination folder
                        shutil.copy2(source_png_file, destination_png_file)
                        print(f'Copied: {source_png_file} to {destination_png_file}')

copy_fbx_files()
