"""YAML loader for the simple_workflow_engine package.

This module provides `load_workflow_from_yaml(path)` which reads a YAML file
containing a top-level `workflow` mapping and returns a `Workflow` instance.

Expected YAML structure:

workflow:
  name: ...
  description: ...
  defaults: { ... }
  steps:
    - id: ...
      module: ...
      function: ...
      needs: [ ... ]
      args: { ... }

The loader validates that `workflow.steps` is a list and that each step is a mapping,
and raises `ValueError` for malformed inputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from .model import Workflow, Step


def load_workflow_from_yaml(path: str | Path) -> Workflow:
    """
    Load a Workflow definition from a YAML file.

    Expected YAML structure:

    workflow:
      name: ...
      description: ...
      defaults: { ... }
      steps:
        - id: ...
          module: ...
          function: ...
          needs: [ ... ]
          args: { ... }

    :param path: Path to the YAML file.
    :return: Workflow instance.
    """
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if "workflow" not in data:
        raise ValueError("YAML must contain top-level key 'workflow'")

    wf_data: Dict[str, Any] = data["workflow"]

    name = wf_data.get("name")
    description = wf_data.get("description")
    defaults = wf_data.get("defaults") or {}
    steps_data = wf_data.get("steps") or []

    if not isinstance(steps_data, list):
        raise ValueError("'workflow.steps' must be a list")

    steps: list[Step] = []
    for raw_step in steps_data:
        if not isinstance(raw_step, dict):
            raise ValueError("Each item in 'workflow.steps' must be a mapping")

        step = Step(
            id=raw_step.get("id", ""),
            module=raw_step.get("module", ""),
            function=raw_step.get("function", ""),
            needs=raw_step.get("needs") or [],
            args=raw_step.get("args") or {},
        )
        steps.append(step)

    workflow = Workflow(
        name=name,
        description=description,
        defaults=defaults,
        steps=steps,
    )

    return workflow
