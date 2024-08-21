#!/usr/bin/env python3

import argparse
import shutil
import os
import re
from pxr import Usd, UsdGeom, UsdOntology

def clean_up(in_usd: str, out_usd: str) -> None:
    stage = Usd.Stage.Open(in_usd)

    keep_prims = {}

    for xform_prim in [prim for prim in stage.TraverseAll() if prim.IsA(UsdGeom.Xform)]:
        if xform_prim.HasAPI(UsdOntology.SemanticTagAPI):
            semanticTagAPI = UsdOntology.SemanticTagAPI(xform_prim)
            for prim_path in semanticTagAPI.GetSemanticLabelsRel().GetTargets():
                prim = stage.GetPrimAtPath(prim_path)
                if prim not in keep_prims:
                    rdf_api = UsdOntology.RdfAPI(prim)
                    keep_prims[prim] = [rdf_api.GetRdfConceptNameAttr().Get(), 
                                        rdf_api.GetRdfNamespaceAttr().Get(),
                                        rdf_api.GetRdfDefinitionAttr().Get()]

            for prim_path in semanticTagAPI.GetSemanticReportsRel().GetTargets():
                prim = stage.GetPrimAtPath(prim_path)
                if prim not in keep_prims:
                    rdf_api = UsdOntology.RdfAPI(prim)
                    keep_prims[prim] = [rdf_api.GetRdfConceptNameAttr().Get(), 
                                        rdf_api.GetRdfNamespaceAttr().Get(),
                                        rdf_api.GetRdfDefinitionAttr().Get()]

    for prim in stage.GetPseudoRoot().GetChildren():
        if any([child_prim.IsAbstract() for child_prim in prim.GetAllChildren()]):
            stage.RemovePrim(prim.GetPath())

    for prim in keep_prims:
        class_prim = stage.CreateClassPrim(prim.GetPath())
        rdf_api = UsdOntology.RdfAPI.Apply(class_prim)
        rdf_api.CreateRdfConceptNameAttr().Set(keep_prims[prim][0])
        rdf_api.CreateRdfNamespaceAttr().Set(keep_prims[prim][1])
        if isinstance(keep_prims[prim][2], str):
            rdf_api.CreateRdfDefinitionAttr().Set(keep_prims[prim][2])

    print(f"Writing to {out_usd}")
    stage.GetRootLayer().Export(out_usd)


def main():
    parser = argparse.ArgumentParser(description="Auto semantic tagging based on object names")
    parser.add_argument("--in_usd", type=str, required=True, help="Input USD")
    parser.add_argument("--out_usd", type=str, required=True, help="Output USD")
    args = parser.parse_args()
    clean_up(args.in_usd, args.out_usd)


if __name__ == "__main__":
    main()