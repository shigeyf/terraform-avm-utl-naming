"""
extract_res_names.py:
Extract resource name parameters from OpenAPI JSON files.
"""

import json


def resolve_ref(ref, spec):
    """Resolve a local $ref in the OpenAPI spec and return the referenced object."""
    if not ref.startswith("#/"):
        return None
    parts = ref.lstrip("#/").split("/")
    obj = spec
    for part in parts:
        obj = obj.get(part)
        if obj is None:
            return None
    return obj


def get_path_last(path):
    """Get the last part of the path, which is expected to be a resource name."""
    split_path = path.split("/")
    return split_path[-1]


def get_param_spec(target, parameters, spec):
    """Get the parameter specification for a given target resource name."""
    ref_name = target[0].upper() + target[1:] + "Parameter"
    for param in parameters:
        is_direct = param.get("name", "") == target
        is_ref = param.get("$ref", "").endswith(ref_name)

        if is_direct:
            return param
        elif is_ref:
            return resolve_ref(param["$ref"], spec)

    return None


def gen_index_containing_substring(lst, substr):
    """Find the index of the first element in the list that contains the substring."""
    for i, item in enumerate(lst):
        if substr in item:
            return i
    return -1


def extract_res_names(openapi_json):
    """Extract resource name parameters from OpenAPI JSON."""
    with open(openapi_json, "r") as f:
        spec = json.load(f)

    name_params = []
    for path, methods in spec.get("paths", {}).items():
        if not path.startswith("/subscriptions/"):
            continue
        for method, op in methods.items():
            plast = get_path_last(path)

            # Target API paths are:
            # 1. Path method is "POST" or "PUT"
            # 2. Path end with a parameter in curly braces (e.g., "{resourceName}")
            if (
                method.lower() in ("post", "put")
                and plast.startswith("{")
                and plast.endswith("}")
            ):
                if not "Name" in plast: # Skip if "Name" is not in the parameter
                    continue

                param_name = plast[1:-1]  # Remove the curly braces
                param_spec = get_param_spec(param_name, op.get("parameters", []), spec)
                if param_spec is None:
                    continue

                depth = len(path.split("/")) - gen_index_containing_substring(path.split("/"), "providers") - 2
                name_params.append(
                    {"name": param_name, "path": path, "path_depth": depth, "spec": param_spec}
                )
                # DEBUG print:
                # print(f"  - param: {param_name}")
                # print(f"    path: {path}")
                # print(f"    spec: {param_spec}")

    return name_params


# if __name__ == "__main__":
#    if len(sys.argv) != 2:
#        print("Usage: python extract_res_names.py <openapi.json>")
#    else:
#        extract_res_names(sys.argv[1])
