"""Small, JSON-compatible evaluation records and errors.

They live with the reference loader in DCP-Bench Open, at
bench/dcp_bench/results.py, so an EvaluationError raised while loading a
reference is the same class the evaluator catches.
"""
from bench.dcp_bench.results import EvaluationError, canonical, digest, strict_json

__all__ = ["EvaluationError", "canonical", "digest", "strict_json"]
