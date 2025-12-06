# python
"""Workflow engine for executing `Workflow` definitions.

This module provides `WorkflowEngine`, a simple executor that runs workflow
steps in dependency order.

Key behaviors:
- Performs a topological sort of steps and detects cycles (`CycleError`).
- Validates that each step's declared dependencies exist (`MissingDependencyError`).
- Resolves callables from an optional `callables` mapping or by dynamic import.
- Merges `workflow.defaults` with each step's `args` (step args take precedence).
- Supplies accumulated prior step results via a reserved `results` kwarg.
- Raises `ExecutionError` when a step cannot be resolved or fails during execution.

Usage: instantiate `WorkflowEngine` and call its `run(workflow)` method to
execute the workflow and receive a mapping of step id -> result.
""""""Workflow engine for executing `Workflow` definitions.

This module provides `WorkflowEngine`, a simple executor that runs workflow
steps in dependency order.

Key behaviors:
- Performs a topological sort of steps and detects cycles (`CycleError`).
- Validates that each step's declared dependencies exist (`MissingDependencyError`).
- Resolves callables from an optional `callables` mapping or by dynamic import.
- Merges `workflow.defaults` with each step's `args` (step args take precedence).
- Supplies accumulated prior step results via a reserved `results` kwarg.
- Raises `ExecutionError` when a step cannot be resolved or fails during execution.

Usage: instantiate `WorkflowEngine` and call its `run(workflow)` method to
execute the workflow and receive a mapping of step id -> result.
"""
from __future__ import annotations

import importlib
from collections import deque, defaultdict
from typing import Any, Callable, Dict, List, Set

from .model import Workflow, Step


# pylint: disable=too-few-public-methods
class WorkflowError(Exception):
    """Base class for workflow engine errors."""


# pylint: disable=too-few-public-methods
class CycleError(WorkflowError):
    """Raised when a cyclic dependency is detected."""


# pylint: disable=too-few-public-methods
class MissingDependencyError(WorkflowError):
    """Raised when a step depends on a missing step."""


class ExecutionError(WorkflowError):
    """Raised when a step execution fails."""


class WorkflowEngine:
    """
    Simple workflow engine that executes steps in dependency order.

    Parameters
    ----------
    callables : dict[str, Callable], optional
        Optional mapping of fully-qualified names ("module.function") to callables.
        These override dynamic import when provided.
    """

    def __init__(self, callables: Dict[str, Callable] | None = None) -> None:
        self.callables = callables or {}

    def _step_map(self, workflow: Workflow) -> Dict[str, Step]:
        return {s.id: s for s in workflow.steps}

    def _topological_order(self, workflow: Workflow) -> List[Step]:
        steps = self._step_map(workflow)
        # Build adjacency: edge from dependency -> dependant
        adj: Dict[str, Set[str]] = defaultdict(set)
        in_degree: Dict[str, int] = {step_id: 0 for step_id in steps}

        for step in steps.values():
            for dep in step.needs:
                if dep not in steps:
                    raise MissingDependencyError(f"Step "
                                                 f"'{step.id}' depends on unknown step '{dep}'")
                adj[dep].add(step.id)
                in_degree[step.id] += 1

        # Kahn's algorithm
        q = deque([nid for nid, deg in in_degree.items() if deg == 0])
        ordered_ids: List[str] = []

        while q:
            nid = q.popleft()
            ordered_ids.append(nid)
            for dependent in adj.get(nid, ()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    q.append(dependent)

        if len(ordered_ids) != len(steps):
            raise CycleError("Cyclic dependency detected among steps")

        return [steps[sid] for sid in ordered_ids]

    def _resolve_callable(self, step: Step) -> Callable:
        fq = f"{step.module}.{step.function}"
        if fq in self.callables:
            return self.callables[fq]

        try:
            module = importlib.import_module(step.module)
            func = getattr(module, step.function)
        except Exception as exc:
            raise ExecutionError(f"Cannot resolve callable for step '{step.id}': {fq}") from exc

        if not callable(func):
            raise ExecutionError(f"Resolved object for step '{step.id}' is not callable: {fq}")

        return func

    def run(self, workflow: Workflow) -> Dict[str, Any]:
        """
        Execute the workflow and return a mapping of step id -> result.

        Raises
        ------
        MissingDependencyError, CycleError, ExecutionError
        """
        ordered_steps = self._topological_order(workflow)
        results: Dict[str, Any] = {}

        for step in ordered_steps:
            func = self._resolve_callable(step)

            # Merge defaults and step args; step args override defaults
            kwargs = {}
            if workflow.defaults:
                kwargs.update(workflow.defaults)
            if step.args:
                kwargs.update(step.args)

            # Optionally, a step may need results of previous steps;
            # provide `results` as a reserved kwarg
            # without clobbering user-specified arg named 'results'
            if 'results' not in kwargs:
                kwargs['results'] = results

            try:
                result = func(**kwargs)
            except Exception as exc:
                raise ExecutionError(f"Step '{step.id}' failed during execution") from exc

            results[step.id] = result

        return results
