# autoref: a PyCSP3 model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python autoref.py autoref.json

from pycsp3 import *


def create_model(instance):
    """Find a self-describing series S = (s0, s1, ..., sn, sn+1) of integers between 0 and n such
    that each integer i from 0 to n occurs exactly s_i times in S, and sn+1 = m."""
    n = instance["n"]  # the largest value in the series
    m = instance["m"]  # the last term of the series, sn+1

    n_terms = n + 2                # the series has n + 2 terms: s0 .. sn and sn+1
    n_values = n + 1               # the values 0 .. n

    # s[i] is the i-th term of the series, an integer between 0 and n.
    s = VarArray(size=n_terms, dom=range(n_values))

    satisfy(
        # Each integer i from 0 to n occurs in S exactly s[i] times.
        [Count(s, value=i) == s[i] for i in range(n_values)],
        # The last term is m.
        s[n + 1] == m,
    )

    return {"s": s}


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
