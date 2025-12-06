from simple_workflow_engine import __about__


def test_version_is_defined_and_non_empty():
    assert hasattr(__about__, "__version__")
    assert isinstance(__about__.__version__, str)
    assert __about__.__version__ != ""


def test_author_is_defined_and_non_empty():
    assert hasattr(__about__, "__author__")
    assert isinstance(__about__.__author__, str)
    assert __about__.__author__ != ""


def test_all_exports_are_consistent():
    # __all__ should exist and list the public names
    assert hasattr(__about__, "__all__")
    assert isinstance(__about__.__all__, (list, tuple))

    for name in __about__.__all__:
        assert hasattr(__about__, name), f"__all__ exports unknown name: {name}"
