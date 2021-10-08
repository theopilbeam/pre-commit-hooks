#!/usr/bin/env python3

import sys
import json
from typing import Dict, Any, List


def log(message: str, end: str = "\n") -> None:
    """Simple logging straight to stderr"""

    sys.stderr.write(message + end)
    sys.stderr.flush()


class DictCleaner:
    keys_ignored: List[str] = []
    keys_none_default: List[str] = []
    keys_empty_list_default: List[str] = []

    @classmethod
    def clean(cls, d: Dict[str, Any]) -> Dict[str, Any]:
        """Will mutate the dict passed"""

        d = cls._clean_ignored_keys(d)
        d = cls._clean_none_default_keys(d)
        d = cls._clean_empty_list_default_keys(d)

        return d

    @classmethod
    def _clean_ignored_keys(cls, d: Dict[str, Any]) -> Dict[str, Any]:
        for k in cls.keys_ignored:
            if k in d:
                log(f"Removing {k} as it's ignored")
                del d[k]

        return d

    @classmethod
    def _clean_none_default_keys(cls, d: Dict[str, Any]) -> Dict[str, Any]:
        for k in cls.keys_none_default:
            if k in d and d[k] is None:
                log(f"Removing {k} as it's the default (`null`)")
                del d[k]

        return d

    @classmethod
    def _clean_empty_list_default_keys(cls, d: Dict[str, Any]) -> Dict[str, Any]:
        for k in cls.keys_empty_list_default:
            if k in d and type(d[k]) == list and len(d[k]) == 0:
                log(f"Removing {k} as it's the default (`[]`)")
                del d[k]

        return d


class TaskDefinitionCleaner(DictCleaner):
    # Keys ignored by the `RegisterTaskDefinition` API
    keys_ignored = [
        "compatibilities",
        "taskDefinitionArn",
        "requiresAttributes",
        "revision",
        "status",
        "registeredAt",
        "deregisteredAt",
        "registeredBy",
    ]
    # Keys whose defaults are `null`.  If set to this value, they can be safely removed
    keys_none_default = [
        "cpu",
        "ephemeralStorage",
        "executionRoleArn",
        "inferenceAccelerators",
        "ipcMode",
        "memory",
        "networkMode",
        "pidMode",
        "placementConstraints",
        "proxyConfiguration",
        "requiresCompatibilities",
        "tags",
        "taskRoleArn",
        "volumes",
    ]
    # Keys whose defaults are `[]`.  If set to this value, they can be safely removed
    keys_empty_list_default = [
        "placementConstraints",
        "requiresCompatibilities",
        "tags",
        "volumes",
    ]

    @classmethod
    def clean(cls, task_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Will mutate the `task_definition` passed"""

        task_definition = super().clean(task_definition)

        task_definition["containerDefinitions"] = [
            ContainerDefinitionCleaner.clean(container_definition)
            for container_definition in task_definition["containerDefinitions"]
        ]

        return task_definition


class ContainerDefinitionCleaner(DictCleaner):
    keys_none_default = [
        "command",
        "cpu",
        "dependsOn",
        "disableNetworking",
        "dnsSearchDomains",
        "dnsServers",
        "dockerLabels",
        "dockerSecurityOptions",
        "entryPoint",
        "environment",
        "environmentFiles",
        "essential",
        "extraHosts",
        "firelensConfiguration",
        "healthCheck",
        "hostname",
        "image",
        "interactive",
        "links",
        "linuxParameters",
        "logConfiguration",
        "memory",
        "memoryReservation",
        "mountPoints",
        "name",
        "portMappings",
        "privileged",
        "pseudoTerminal",
        "readonlyRootFilesystem",
        "repositoryCredentials",
        "resourceCredentials",
        "resourceRequirements",
        "secrets",
        "startTimeout",
        "stopTimeout",
        "systemControls",
        "ulimits",
        "user",
        "volumesFrom",
        "workingDirectory",
    ]
    keys_empty_list_default = [
        "dependsOn",
        "dnsSearchDomains",
        "dnsServers",
        "dockerSecurityOptions",
        "environment",
        "environmentFiles",
        "extraHosts",
        "links",
        "mountPoints",
        "portMappings",
        "resourceRequirements",
        "secrets",
        "systemControls",
        "ulimits",
        "volumesFrom",
    ]


if __name__ == "__main__":
    # This script is called by pre-commit, and so we have to follow its rules:

    # - The script is called with one (or more) paths as its arguments
    # - The script should modify those files, if it needs to
    #   - If modifications are made, the script _must_ exit with a
    #     non-zero status code
    #   - If no changes are made, the script _must_ exit with a zero
    #     status code

    # Specifically in our case, other commit hooks (JSON formatting)
    # means that the output of this script is not valid.  This means
    # if we're not making real changes to the JSON document, we
    # shouldn't modify the file.  Put differently, we shouldn't output
    # only differences in formatting or ordering of the document.

    # Tracking whether any changes are made
    changes_made = False

    for f_path in sys.argv[1:]:
        with open(f_path) as f:
            task_def_str = f.read()

        task_def = json.loads(task_def_str)
        # to JSON with known settings so we can figure out if we change anything
        task_def_str = json.dumps(task_def, indent=4, sort_keys=True)

        clean_task_def = TaskDefinitionCleaner.clean(task_def)
        clean_task_def_str = json.dumps(clean_task_def, indent=4, sort_keys=True)

        if clean_task_def_str != task_def_str:
            changes_made = True

            with open(f_path, "w") as f:
                f.write(clean_task_def_str)

    exit(int(changes_made))
