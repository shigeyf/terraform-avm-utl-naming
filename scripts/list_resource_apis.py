"""
list_resource_apis.py:
Crawl the Azure REST API specification folder to find resource manager APIs.
"""

import os
import re


PATH_DEPTH = 5


def list_resource_manager_apis(root_dir):
    """Crawl the Azure REST API specification folder to find resource manager APIs."""

    root_depth = len(root_dir.split(os.sep))
    print(f"Root depth: {root_depth}")
    resource_manager_api_dict = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        parts = dirpath.split(os.sep)

        # Check the folder
        # <spec-root>/<folder>/resource-manager/
        #   <PROVIDER>/stable or preview/<VERSION>/
        if len(parts) == (root_depth + PATH_DEPTH) and parts[-4] == "resource-manager":
            provider = {}
            if re.match(r"^Microsoft\.*", parts[-3]) and (
                parts[-2] == "stable" #or parts[-2] == "preview"
            ):
                provider["provider_name"] = parts[-3]
                provider["api_version"] = parts[-1]
                parts.pop()
                parts.pop()
                provider["path"] = os.sep.join(parts).replace(root_dir, "")

                if provider["path"] not in resource_manager_api_dict:
                    resource_manager_api_dict[provider["path"]] = {
                        "path": provider["path"],
                        "name": provider["provider_name"],
                        "api_versions": [],
                    }
                resource_manager_api_dict[provider["path"]]["api_versions"].append(
                    provider["api_version"]
                )

        # Check the folder
        # <spec-root>/<folder>/resource-manager/
        #   <PROVIDER>/<sub-folder>/stable or preview/<VERSION>/
        if len(parts) == (root_depth + PATH_DEPTH + 1) and parts[-5] == "resource-manager":
            provider = {}
            if re.match(r"^Microsoft\.*", parts[-4]) and (
                parts[-2] == "stable" #or parts[-2] == "preview"
            ):
                provider["provider_name"] = f"{parts[-4]}.{parts[-3]}"
                provider["api_version"] = parts[-1]
                parts.pop()
                parts.pop()
                provider["path"] = os.sep.join(parts).replace(root_dir, "")

                if provider["path"] not in resource_manager_api_dict:
                    resource_manager_api_dict[provider["path"]] = {
                        "path": provider["path"],
                        "name": provider["provider_name"],
                        "api_versions": [],
                    }
                resource_manager_api_dict[provider["path"]][
                    "api_versions"
                ].append(provider["api_version"])

    resource_manager_api_list = [
        {"path": k, "properties": v}
        for k, v in resource_manager_api_dict.items()
    ]
    # Sort by provider, then api_version
    resource_manager_api_list.sort(key=lambda x: (x["path"]))
    for p in resource_manager_api_list:
        p["properties"]["api_versions"].sort()
    return resource_manager_api_list
