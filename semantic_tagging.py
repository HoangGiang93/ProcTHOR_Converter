#!/usr/bin/env python3

import argparse
import shutil
import os
import re
from pxr import Usd, UsdGeom, UsdOntology


sem_TBox = {}

ignore_classes = {
    "animal"
}

synonyms = {
    "Fridge": "Refrigerator",
}


def auto_sem_tag(in_ABox_usd_file: str, in_TBox_Usd_file: str, out_ABox_usd_file: str) -> None:
    tmp_out_ABox_usd_file = os.path.join(os.path.dirname(in_ABox_usd_file), "tmp.usda")
    shutil.copy(src=in_ABox_usd_file, dst=tmp_out_ABox_usd_file)

    stage_TBox = Usd.Stage.Open(in_TBox_Usd_file)
    for prim in stage_TBox.Traverse():
        for prim_class in prim.GetAllChildren():
            if not any([ignore_class in prim_class.GetName() for ignore_class in ignore_classes]):
                sem_TBox[prim_class.GetName()] = prim_class.GetPrimPath()

    stage_ABox = Usd.Stage.Open(tmp_out_ABox_usd_file)
    stage_ABox.GetRootLayer().subLayerPaths = [in_TBox_Usd_file]

    for prim in stage_ABox.Traverse():
        prepended_items = prim.GetPrim().GetPrimStack()[0].referenceList.prependedItems
        if len(prepended_items) == 1:
            prim.GetPrim().GetReferences().ClearReferences()
            mesh_dir_abs_path = prepended_items[0].assetPath
            prim_path = prepended_items[0].primPath
            if not os.path.isabs(mesh_dir_abs_path):
                if mesh_dir_abs_path[:2] == "./":
                    mesh_dir_abs_path = mesh_dir_abs_path[2:]
                mesh_dir_abs_path = os.path.join(os.path.dirname(in_ABox_usd_file), mesh_dir_abs_path)
            prim.GetPrim().GetReferences().AddReference(mesh_dir_abs_path, prim_path)
        elif len(prepended_items) > 1:
            mesh_dir_abs_paths = []
            prim_paths = []
            for prepended_item in prepended_items:
                mesh_dir_abs_path = prepended_item.assetPath
                prim_paths.append(prepended_item.primPath)
                if not os.path.isabs(mesh_dir_abs_path):
                    if mesh_dir_abs_path[:2] == "./":
                        mesh_dir_abs_path = mesh_dir_abs_path[2:]
                    mesh_dir_abs_path = os.path.join(os.path.dirname(in_ABox_usd_file), mesh_dir_abs_path)
                mesh_dir_abs_paths.append(mesh_dir_abs_path)
            prim.GetPrim().GetReferences().ClearReferences()
            for mesh_dir_abs_path, prim_path in zip(mesh_dir_abs_paths, prim_paths):
                prim.GetPrim().GetReferences().AddReference(mesh_dir_abs_path, prim_path)

        if prim.IsA(UsdGeom.Xform):
            prim_name = prim.GetName().replace("surface", "")
            prim_name = ''.join(filter(str.isalpha, prim_name))
            if prim_name in synonyms:
                prim_name = synonyms[prim_name]

            SOMA_DFL_sem_classes = []
            SOMA_sem_classes = []
            for sem_class_name, sem_class in sem_TBox.items():
                if sem_class_name.lower() == f"_class_{prim_name}".lower():
                    if "SOMA_DFL" == sem_class.GetParentPath().name:
                        SOMA_DFL_sem_classes.append(sem_class)
                    elif "SOMA" == sem_class.GetParentPath().name:
                        SOMA_sem_classes.append(sem_class)

            if len(SOMA_DFL_sem_classes) == 0:
                for sem_class_name, sem_class in sem_TBox.items():
                    if f"_class_{prim_name.lower()}" == "_".join(sem_class_name.split("nwn")[:-1]).lower():
                        SOMA_DFL_sem_classes.append(sem_class)

            # Split name into words
            words = re.findall('[A-Z][^A-Z]*', prim_name)
            if len(SOMA_DFL_sem_classes) == 0 and len(words) > 1:
                for sem_class_name, sem_class in sem_TBox.items():
                    if f"_class_{'_'.join(words).lower()}" == "_".join(sem_class_name.split("nwn")[:-1]).lower():
                        SOMA_DFL_sem_classes.append(sem_class)

            if len(SOMA_DFL_sem_classes) == 0 and len(words) > 1:
                for sem_class_name, sem_class in sem_TBox.items():
                    if f"_class_{words[-1].lower()}" == "_".join(sem_class_name.split("nwn")[:-1]).lower():
                        SOMA_DFL_sem_classes.append(sem_class)

            if len(SOMA_sem_classes) == 0 and len(SOMA_DFL_sem_classes) == 0:
                print(f"prim_name: {prim_name} is not in sem_TBox")
            
            semanticTagAPI = UsdOntology.SemanticTagAPI.Apply(prim)

            if len(SOMA_sem_classes) > 0:
                SOMA_sem_class = SOMA_sem_classes[0]
                print(f"prim_name: {prim_name} is in sem_class: {SOMA_sem_class.name}")
                semanticTagAPI.CreateSemanticLabelsRel().AddTarget(SOMA_sem_class)

            if len(SOMA_DFL_sem_classes) > 0:
                SOMA_DFL_sem_class = SOMA_DFL_sem_classes[0]
                for sem_class in SOMA_DFL_sem_classes:
                    if "furniture" in sem_class.name:
                        SOMA_DFL_sem_class = sem_class
                        break
                print(f"prim_name: {prim_name} is in sem_class: {SOMA_DFL_sem_class.name}")
                semanticTagAPI.CreateSemanticLabelsRel().AddTarget(SOMA_DFL_sem_class)

    print(f"Save usd stage to {out_ABox_usd_file} that has semantic labels from {in_TBox_Usd_file}")
    stage_ABox.GetRootLayer().Save()
    os.rename(tmp_out_ABox_usd_file, out_ABox_usd_file)

    return None


def main():
    parser = argparse.ArgumentParser(description="Auto semantic tagging based on object names")
    parser.add_argument("--in_usd", type=str, required=True, help="Input USD")
    parser.add_argument("--in_TBox_usd", type=str, required=True, help="Input TBox USD")
    parser.add_argument("--out_ABox_usd", type=str, required=True, help="Output ABox USD")
    args = parser.parse_args()
    auto_sem_tag(args.in_usd, args.in_TBox_usd, args.out_ABox_usd)


if __name__ == "__main__":
    main()
