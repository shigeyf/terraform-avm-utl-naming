"""
This script generates a single-merged OpenAPI specifications
 per Azure Resource by crawling through resource manager API specifications.

To run this module, use the following command:
  python3 ./scripts/tool_gen_openapi_specs.py --crawl <specification_root_folder>

"""

import sys
import os
from list_resource_apis import list_resource_manager_apis
from merge_openapi_jsons import merge_open_api_jsons


gen_path = "./generated"


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--crawl":
        spec_root = sys.argv[2]

        for p in list_resource_manager_apis(spec_root):

            api_base_path = p["properties"]["path"]
            api_provider = p["properties"]["name"]
            api_version = p["properties"]["api_versions"][-1]
            print(f"==> Processing {api_base_path} ({api_provider}:{api_version})")

            path = api_base_path + "/stable/" + api_version
            if "preview" in api_version:
                path = api_base_path + "/preview/" + api_version

            #split_path = path.split(os.sep)
            #del split_path[:3]
            #print(f" > Path: {os.sep.join(split_path)}")
            merge_open_api_jsons(path, api_provider, api_version, spec_root, gen_path)

    else:
        print("Usage:")
        print(
            "  python extract_create_api_parameters.py --crawl <specification_root_folder>"
        )
