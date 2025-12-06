# python
from pathlib import Path

import pytest

from simple_workflow_engine.yaml_loader import load_workflow_from_yaml


def test_load_valid_workflow(tmp_path: Path):
    yaml_content = """
workflow:
  name: example
  description: An example workflow
  defaults:
    retry: 3
  steps:
    - id: step1
      module: mymod
      function: do_work
      needs: [prev_step]
      args:
        param: 1
"""
    p = tmp_path / "valid.yaml"
    p.write_text(yaml_content, encoding="utf-8")

    wf = load_workflow_from_yaml(p)

    assert wf.name == "example"
    assert wf.description == "An example workflow"
    assert wf.defaults == {"retry": 3}
    assert len(wf.steps) == 1

    step = wf.steps[0]
    assert step.id == "step1"
    assert step.module == "mymod"
    assert step.function == "do_work"
    assert step.needs == ["prev_step"]
    assert step.args == {"param": 1}


def test_missing_workflow_key_raises(tmp_path: Path):
    yaml_content = """
not_workflow:
  name: no
"""
    p = tmp_path / "no_workflow.yaml"
    p.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="top-level key 'workflow'"):
        load_workflow_from_yaml(p)


def test_steps_not_list_raises(tmp_path: Path):
    yaml_content = """
workflow:
  name: bad
  steps: not-a-list
"""
    p = tmp_path / "bad_steps.yaml"
    p.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="'workflow.steps' must be a list"):
        load_workflow_from_yaml(p)


def test_step_not_mapping_raises(tmp_path: Path):
    yaml_content = """
workflow:
  name: bad_item
  steps:
    - not-a-mapping
"""
    p = tmp_path / "bad_item.yaml"
    p.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="Each item in 'workflow.steps' must be a mapping"):
        load_workflow_from_yaml(p)
