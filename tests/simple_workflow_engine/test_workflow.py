import pytest

from simple_workflow_engine.model import Workflow, Step


def test_workflow_minimal():
    wf = Workflow(name="test_workflow")

    assert wf.name == "test_workflow"
    assert wf.description is None
    assert wf.defaults == {}
    assert wf.steps == []


def test_workflow_with_defaults_and_steps():
    steps = [
        Step(
            id="step1",
            module="example.module",
            function="func1",
        ),
        Step(
            id="step2",
            module="example.module",
            function="func2",
            needs=["step1"],
            args={"x": 1},
        ),
    ]

    wf = Workflow(
        name="etl_workflow",
        description="ETL pipeline",
        defaults={"run_id": "123", "owner": "data-team"},
        steps=steps,
    )

    assert wf.name == "etl_workflow"
    assert wf.description == "ETL pipeline"
    assert wf.defaults["run_id"] == "123"
    assert wf.defaults["owner"] == "data-team"
    assert len(wf.steps) == 2
    assert wf.steps[0].id == "step1"
    assert wf.steps[1].needs == ["step1"]
    assert wf.steps[1].args == {"x": 1}


def test_workflow_normalizes_none_defaults_and_steps():
    wf = Workflow(
        name="normalize_workflow",
        description="check None behavior",
        defaults=None,  # type: ignore[arg-type]
        steps=None,     # type: ignore[arg-type]
    )

    assert wf.defaults == {}
    assert wf.steps == []


def test_workflow_requires_name():
    with pytest.raises(ValueError) as excinfo:
        Workflow(name="")  # empty name should fail

    assert "must not be empty" in str(excinfo.value).lower()

def test_step_set_needs_and_args_to_empty_when_none():
    step = Step(
        id="step1",
        module="example.module",
        function="func1",
        needs=None,  # type: ignore[arg-type]
        args=None,   # type: ignore[arg-type]
    )

    assert step.needs == []
    assert step.args == {}