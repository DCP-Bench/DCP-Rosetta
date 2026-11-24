# PyCSP3 star-imports its vocabulary, as every PyCSP3 model does.
# ruff: noqa: F403, F405
from pycsp3 import *


def create_model(instance):
    n = instance["n"]
    x = Var(range(n + 1))
    y = Var(range(n + 1))
    if instance["optimize"]:
        satisfy(x + y >= n)
        minimize(x + y)
    else:
        satisfy(x + y == n)
    return {"x": x, "y": y}
