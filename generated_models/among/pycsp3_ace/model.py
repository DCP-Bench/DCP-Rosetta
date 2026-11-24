# among: a PyCSP3 model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python among.py among.json

from pycsp3 import *


def create_model(instance):
    """Find an array x of n integers between 0 and 7, inclusive, such that exactly m
    of them take one of the values in v. The other elements may take any other value
    in that range."""
    n = instance["n"]    # the number of elements of x
    m = instance["m"]    # how many elements of x must take one of the values in v
    v = instance["v"]    # the values that the counted elements take
    max_value = 7        # the values of x lie between 0 and max_value, inclusive, as the problem states

    # The distinct values of v (a repeated value in v must not be counted twice).
    distinct_v = sorted(set(v))

    # x[i] is element i of x: an integer from 0 to max_value, which may or may not be one of the values in v.
    x = VarArray(size=n, dom=range(max_value + 1))

    satisfy(
        # Exactly m elements of x take one of the values in v.
        # Counted with a Sum of equalities rather than Count(x, values=...) == m, because ACE rejects a Count whose total is 0 (Bad value of k=0), and m can be 0.
        Sum(x[i] == value for i in range(n) for value in distinct_v) == m,
    )

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
