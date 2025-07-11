"""
merge_openapi_jsons.py:
Merge multiple OpenAPI definition files into a single OpenAPI JSON file.
"""

import json
import glob
import os
from collections import defaultdict


def merge_open_api_jsons(api_dir, api_provider, api_version, spec_root, output_dir="./generated"):
    """Merge multiple OpenAPI definition files."""

    merged = {
        "openapi": "3.0.0",
        "info": {"title": f"{api_provider}", "version": f"{api_version}"},
        "components": defaultdict(dict),
        "paths": {},
        "parameters": {},
        "definitions": {},
    }

    api_root = spec_root + api_dir
    for filename in glob.glob(f"{api_root}/*.json"):
        print(f"   => Merging {filename.split(os.sep)[-1]}...")
        with open(filename) as f:
            data = json.load(f)
            merged["paths"].update(data.get("paths", {}))
            merged["definitions"].update(data.get("definitions", {}))
            merged["parameters"].update(data.get("parameters", {}))
            for comp_type, comp_obj in data.get("components", {}).items():
                merged["components"][comp_type].update(comp_obj)

    merged["components"] = dict(merged["components"])
    merged["parameters"] = dict(merged["parameters"])

    external_refs = []
    for i in merged["paths"].values():
        for method in i.values():
            if "parameters" in method:
                for param in method["parameters"]:
                    if "$ref" in param:
                        ref = param["$ref"]
                        if ref.startswith("."):
                            ref_parts = ref.split("#")
                            param["$ref"] = f"#{ref_parts[1]}"
                            if ref_parts[0] not in external_refs and ref_parts[0].startswith("../"):
                                external_refs.append(ref_parts[0])

    for ref_name in external_refs:
        filename = os.path.join(api_root, ref_name)
        print(f"   => Merging External Refs {ref_name}...")
        with open(filename) as f:
            data = json.load(f)
            merged["definitions"].update(data.get("definitions", {}))
            merged["parameters"].update(data.get("parameters", {}))

    api_out_dir = f"{output_dir}{api_dir}".replace("/resource-manager", "")
    os.makedirs(f"{api_out_dir}", exist_ok=True)
    with open(f"{api_out_dir}/openapi.json", "w") as f:
        json.dump(merged, f, indent=2)
        print(f" > Output OpenAPI.json: {api_out_dir}/openapi.json")
