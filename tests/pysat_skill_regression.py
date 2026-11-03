"""Regression for the pysat skill's warning that IntegerEngine keeps the list it is given.

Takes a skill bundle path and checks two things:

1. that the defect is real, by running a small script in the pysat image: after
   `IntegerEngine(vars=xs)` and one `engine.add_var(q)`, `xs` holds three Integers
   instead of two, and with `IntegerEngine(vars=list(ys))` `ys` keeps its two, and
2. that the bundle warns about it: some line names `add_var` together with the
   caller's list growing (`append`).

A bundle that does not carry the warning fails, which is what makes this a check
of the instructions rather than of the library alone. The defect cost a
pre-check in the run that produced this script: the pysat model of
`divisible_by_1_through_9` reported its ten digits plus nine quotients
(`generation/runs/20261102-divisible-digits/attempts/divisible_by_1_through_9/pysat/attempt-001/lessons.md`).
"""
import subprocess
import sys
from pathlib import Path

IMAGE = "dcp-eval/pysat:v1"

SCRIPT = """
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
pool = IDPool()
xs = [Integer(f"x{i}", 0, 3, vpool=pool) for i in range(2)]
engine = IntegerEngine(vars=xs, vpool=pool)
engine.add_var(Integer("q", 0, 3, vpool=pool))
ys = [Integer(f"y{i}", 0, 3, vpool=pool) for i in range(2)]
engine = IntegerEngine(vars=list(ys), vpool=pool)
engine.add_var(Integer("r", 0, 3, vpool=pool))
print(len(xs), len(ys))
"""


def defect():
    """(shared length, copied length) measured in the image."""
    result = subprocess.run(["docker", "run", "--rm", "--network", "none", "--entrypoint", "python",
                             IMAGE, "-c", SCRIPT], capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise SystemExit(f"reproducer failed: {result.stderr.strip()}")
    shared, copied = map(int, result.stdout.split())
    return shared, copied


def warns(bundle):
    """True when a text file of the bundle has a line naming add_var and append."""
    for path in Path(bundle).rglob("*"):
        if path.suffix not in {".md", ".json", ".py"} or not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if "add_var" in line and "append" in line:
                return True
    return False


def main():
    bundle = sys.argv[1]
    shared, copied = defect()
    reproduced = shared == 3 and copied == 2
    warned = warns(bundle)
    print(f"defect reproduced: {reproduced} (shared list {shared}, copied list {copied}); skill warns: {warned}")
    return 0 if reproduced and warned else 1


if __name__ == "__main__":
    raise SystemExit(main())
