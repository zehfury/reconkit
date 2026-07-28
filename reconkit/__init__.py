"""
reconkit — a modular web reconnaissance automation framework.

Each submodule collects one category of public data about a target
domain and returns a plain dict. Modules never raise — failures are
caught internally and surfaced as {"error": "..."} inside the result,
so one broken module never takes down the run.
"""

__version__ = "0.1.0"
