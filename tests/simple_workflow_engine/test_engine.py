# python
import pytest

from simple_workflow_engine.model import Workflow, Step
from simple_workflow_engine.engine import (
    WorkflowEngine,
    MissingDependencyError,
    CycleError,
    ExecutionError,
)


def test_run_order_defaults_and_results():
    # callables keyed by "module.function" to avoid dynamic import
    def f_a(x=0, results=None):
        return x + 1

    def f_b(results, y=0):
        # consume prior step result via reserved `results` kwarg
        return results["s1"] + y

    callables = {"fake.f_a": f_a, "fake.f_b": f_b}

    steps = [
        Step(id="s1", module="fake", function="f_a", needs=[], args={"x": 2}),
        Step(id="s2", module="fake", function="f_b", needs=["s1"], args={"y": 3}),
    ]
    wf = Workflow(name="wf", description="test", defaults={}, steps=steps)

    engine = WorkflowEngine(callables=callables)
    results = engine.run(wf)

    assert results["s1"] == 3
    assert results["s2"] == 6


def test_missing_dependency_raises():
    steps = [Step(id="s1", module="fake", function="f", needs=["missing"], args={})]
    wf = Workflow(name="wf", description="", defaults=None, steps=steps)

    engine = WorkflowEngine()
    with pytest.raises(MissingDependencyError):
        engine.run(wf)


def test_cycle_detection_raises():
    steps = [
        Step(id="a", module="fake", function="fa", needs=["b"], args={}),
        Step(id="b", module="fake", function="fb", needs=["a"], args={}),
    ]
    wf = Workflow(name="wf", description="", defaults=None, steps=steps)

    engine = WorkflowEngine(callables={"fake.fa": lambda **k: 1, "fake.fb": lambda **k: 2})
    with pytest.raises(CycleError):
        engine.run(wf)


def test_non_callable_mapping_raises_execution_error():
    # mapping supplies a non-callable object; calling will raise and be wrapped as ExecutionError
    callables = {"fake.bad": 123}
    steps = [Step(id="s1", module="fake", function="bad", needs=[], args={})]
    wf = Workflow(name="wf", description="", defaults=None, steps=steps)

    engine = WorkflowEngine(callables=callables)
    with pytest.raises(ExecutionError):
        engine.run(wf)


def test_unresolvable_import_raises_execution_error():
    steps = [Step(id="s1", module="nonexistent.module", function="f", needs=[], args={})]
    wf = Workflow(name="wf", description="", defaults=None, steps=steps)

    engine = WorkflowEngine()
    with pytest.raises(ExecutionError):
        engine.run(wf)


def test_step_exception_is_wrapped_in_execution_error():
    def bad(**kwargs):
        raise ValueError("boom")

    callables = {"fake.bad": bad}
    steps = [Step(id="s1", module="fake", function="bad", needs=[], args={})]
    wf = Workflow(name="wf", description="", defaults=None, steps=steps)

    engine = WorkflowEngine(callables=callables)
    with pytest.raises(ExecutionError):
        engine.run(wf)