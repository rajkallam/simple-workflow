from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Step:
    """
    Represents a single workflow step.

    Attributes
    ----------
    id : str
        Unique identifier for this step.
    module : str
        Module path where the function is located.
    function : str
        Name of the function inside the module.
    needs : list[str]
        List of step IDs that must run before this step.
    args : dict[str, Any]
        Dictionary of keyword arguments passed to the function.
    """

    id: str
    module: str
    function: str
    needs: List[str] = field(default_factory=list)
    args: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            raise ValueError("Step 'id' must not be empty")
        if not self.module:
            raise ValueError("Step 'module' must not be empty")
        if not self.function:
            raise ValueError("Step 'function' must not be empty")

        if self.needs is None:
            self.needs = []

        if self.args is None:
            self.args = {}


@dataclass
class Workflow:
    """
    Represents a workflow definition.
    """

    name: str
    description: Optional[str] = None
    defaults: Dict[str, Any] = field(default_factory=dict)
    steps: List[Step] = field(default_factory=list)

    def __post_init__(self):
        if not self.name:
            raise ValueError("Workflow 'name' must not be empty")

        if self.defaults is None:
            self.defaults = {}

        if self.steps is None:
            self.steps = []
