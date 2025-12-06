# simple-workflow

Simple workflow to execute Python functions with dependency resolution.

## Overview
Lightweight pattern to run Python callables and automatically provide their dependencies by inspecting function parameters and resolving them from a registry of providers.

## Features
- Resolve and inject dependencies based on function parameter names.
- Minimal example to illustrate the pattern.
- Easy to extend for real projects.

## Installation
Clone the repository and install dependencies (if any):

```bash
git clone https://github.com/rajkallam/simple-workflow.git
cd simple-workflow
python -m pip install . 