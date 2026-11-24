# csplib_074_maximum_clique: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

from docplex.mp.model import Model


def create_model(instance):
    """Maximum clique: choose as many vertices as possible such that every two of them are adjacent."""
    n = instance["n"]      # number of vertices
    adj = instance["adj"]  # adj[i][j] is 1 when vertices i and j are connected by an edge

    model = Model("maximum_clique")

    # c[i] is 1 when vertex i is in the clique.
    c = model.binary_var_list(n, name="c")

    # Two vertices that are not connected cannot both be in the clique. One
    # constraint per vertex covers all its later non-neighbours at once: when i
    # is in the clique, none of them is. The pairwise form needs one constraint
    # per non-edge, 1312 on the largest instance, past the 1000 the Community
    # Edition allows; both forms admit exactly the same cliques.
    for i in range(n):
        later = [j for j in range(i + 1, n) if adj[i][j] == 0]
        if later:
            model.add_constraint(model.sum(c[j] for j in later) <= len(later) * (1 - c[i]),
                                 ctname=f"non_neighbours_{i}")

    # Maximise the size of the clique.
    model.maximize(model.sum(c))

    return model, {"c": c}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
