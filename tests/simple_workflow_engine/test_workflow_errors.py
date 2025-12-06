import pytest
from simple_workflow_engine.model import Workflow, Step


def test_workflow_raises_value_error_when_name_is_empty():
    # "" is invalid
    with pytest.raises(ValueError) as exif:
        Workflow(name="")

    # Ensure error message is meaningful
    assert "must not be empty" in str(exif.value).lower()


def test_step_raises_value_error_when_id_is_empty():
    # "" is invalid
    with pytest.raises(ValueError) as exif:
        Step(id="", module="some.module", function="do_something")

    # Ensure error message is meaningful
    assert "must not be empty" in str(exif.value).lower()


def test_step_raises_value_error_when_module_is_empty():
    # "" is invalid
    with pytest.raises(ValueError) as exif:
        Step(id="a", module="", function="do_something")

    # Ensure error message is meaningful
    assert "must not be empty" in str(exif.value).lower()


def test_step_raises_value_error_when_function_is_empty():
    # "" is invalid
    with pytest.raises(ValueError) as exif:
        Step(id="a", module="some.module", function="")

    # Ensure error message is meaningful
    assert "must not be empty" in str(exif.value).lower()
