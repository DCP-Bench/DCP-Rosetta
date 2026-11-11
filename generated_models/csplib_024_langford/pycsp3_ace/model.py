# csplib_024_langford: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_024_langford.py csplib_024_langford.json

from pycsp3 import *


def create_model(instance):
    """Arrange two copies of each number from 1 to k in one sequence of 2k numbers so that the two 1's
    appear one number apart, the two 2's two numbers apart, and so on up to the two k's, k numbers apart."""
    k = instance["k"]        # the largest number: the sequence holds two copies of each of 1 to k
    n_positions = 2 * k      # the sequence has 2k positions, numbered from 0

    numbers = range(1, k + 1)

    # sol[p] is the number at position p of the sequence
    sol = VarArray(size=n_positions, dom=numbers)
    # first[n - 1] is the position of the first copy of number n; arrays count from 0, so number n is at index n - 1
    first = VarArray(size=k, dom=range(n_positions))
    # second[n - 1] is the position of the second copy of number n
    second = VarArray(size=k, dom=range(n_positions))

    satisfy(
        # The two copies of n have n numbers between them, so they lie n + 1 positions apart.
        [second[n - 1] == first[n - 1] + n + 1 for n in numbers],
        # The first and second copies of n sit at positions of the sequence holding n.
        [sol[first[n - 1]] == n for n in numbers],
        [sol[second[n - 1]] == n for n in numbers],
        # The 2k copies sit at 2k different positions, so each position holds exactly one copy.
        AllDifferent(list(first) + list(second)),
    )

    return {"sol": sol}


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
