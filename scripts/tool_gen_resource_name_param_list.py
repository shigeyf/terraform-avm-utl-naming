"""
This script generates a list of resource name parameters (in YAML format)
 from OpenAPI JSON files in the specified directory structure.

To run this module, use the following command after generating local OpenAPI specs (if not already done):
  python3 ./scripts/tool_gen_resource_name_param_list.py

"""

import os
import yaml
from extract_res_names import extract_res_names

gen_path = "./generated"


if __name__ == "__main__":
    data = {"spec": {}}
    for dirpath, dirnames, filenames in os.walk(gen_path):
        for filename in filenames:
            if filename.endswith(".json"):
                json_path = os.path.join(dirpath, filename)
                name_params = extract_res_names(json_path)
                provider = dirpath.split(os.sep)[-3]
                version = dirpath.split(os.sep)[-1]
                if len(dirpath.split(os.sep)) > 6:
                    provider = dirpath.split(os.sep)[-4]

                if not provider in data["spec"]:
                    data["spec"][provider] = []

                if not name_params == []:
                    data["spec"][f"{provider}"].append(
                        {
                            "version": version,
                            "specpath": dirpath,
                            "zparams": [
                                {
                                    "param": param["name"],
                                    "path": param["path"],
                                    "path_depth": param["path_depth"],
                                    "spec": param["spec"],
                                }
                                for param in name_params
                            ],
                        }
                    )

    print(
        yaml.dump(
            data, allow_unicode=True, indent=2, sort_keys=True, default_flow_style=False
        )
    )
