# session3_farmer_and_cows: a cvc5 (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

import itertools

import cvc5.pythonic as c5


def create_model(instance):
    """A farmer has cows numbered 1 up to the number of cows, and cow i gives milk equal
    to its number. He gives each of his sons a set number of cows, so that every son gets
    the same total milk. Decide which son gets each cow."""
    n_cows = instance["num_cows"]            # the number of cows, numbered 1 to n_cows
    n_sons = instance["num_sons"]            # the number of sons, numbered from 0
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: the number of cows son s gets

    # gets[i][s] is true when son s gets cow i+1
    gets = [[c5.Bool(f"gets_{i}_{s}") for s in range(n_sons)] for i in range(n_cows)]

    solver = c5.Solver()

    # Each cow goes to exactly one son.
    for cow in gets:
        solver.add(c5.Or(cow))
        solver.add([c5.Not(c5.And(a, b)) for a, b in itertools.combinations(cow, 2)])

    # Son s gets cows_per_son[s] cows.
    for s, number in enumerate(cows_per_son):
        solver.add(c5.Sum([c5.If(cow[s], 1, 0) for cow in gets]) == number)

    # Every son gets the same total milk. The cows give 1 + 2 + ... + n_cows in all.
    total_milk = n_cows * (n_cows + 1) // 2
    if total_milk % n_sons != 0:
        # The milk does not split evenly, so no distribution works.
        impossible = c5.Bool("impossible")
        solver.add(c5.And(impossible, c5.Not(impossible)))
    else:
        share = total_milk // n_sons  # the milk each son gets
        for s in range(n_sons):
            solver.add(c5.Sum([c5.If(cow[s], i + 1, 0) for i, cow in enumerate(gets)]) == share)

    # cow_assignments[i] is the son who gets cow i+1.
    cow_assignments = [c5.Sum([c5.If(flag, s, 0) for s, flag in enumerate(cow)]) for cow in gets]

    return solver, {"cow_assignments": cow_assignments}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
