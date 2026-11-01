# csplib_044_steiner: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_044_steiner.py csplib_044_steiner.json

from pychoco.model import Model


def create_model(instance):
    """Find n * (n - 1) / 6 triples of distinct elements of {1, ..., n} such that any two
    triples have at most one element in common, for n that is 1 or 3 modulo 6."""
    n = instance["n"]          # the number of elements
    n_sets = n * (n - 1) // 6  # the number of triples

    model = Model()

    # sets[i][j] is true when element j is part of triple i
    sets = [[model.boolvar(name=f"sets_{i}_{j}") for j in range(n)] for i in range(n_sets)]

    # members[i][p] is the element in position p of triple i, the three positions in increasing order
    members = [[model.intvar(0, n - 1, name=f"members_{i}_{p}") for p in range(3)]
               for i in range(n_sets)]

    # Each triple has exactly three elements, and they are listed in increasing order.
    for i in range(n_sets):
        model.arithm(members[i][0], "<", members[i][1]).post()
        model.arithm(members[i][1], "<", members[i][2]).post()

        # position_flags[p][k] is true when position p of triple i holds element k
        position_flags = []
        for p in range(3):
            flags = [model.boolvar(name=f"position_{i}_{p}_{k}") for k in range(n)]
            model.bools_int_channeling(flags, members[i][p], 0).post()
            position_flags.append(flags)

        # Element k is in triple i when one of the three positions holds k.
        for k in range(n):
            model.sum([position_flags[p][k] for p in range(3)], "=", sets[i][k]).post()
        model.sum(sets[i], "=", 3).post()

    # Two triples share at most one element, so no two pairs of elements repeat across triples.
    # The pair code a * n + b names the pair of elements a < b, and its codes are all different.
    pair_codes = []
    for i in range(n_sets):
        for p, q in [(0, 1), (0, 2), (1, 2)]:
            code = model.intvar([a * n + b for a in range(n) for b in range(a + 1, n)],
                                name=f"pair_code_{i}_{p}{q}")
            model.scalar([members[i][p], members[i][q], code], [n, 1, -1], "=", 0).post()
            pair_codes.append(code)
    model.all_different(pair_codes).post()

    # Implied: each element lies in (n - 1) / 2 triples, since its n - 1 pairs each lie in
    # exactly one triple and a triple takes two of them.
    for k in range(n):
        model.sum([sets[i][k] for i in range(n_sets)], "=", (n - 1) // 2).post()

    return model, {"sets": sets}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
