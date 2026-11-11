# session2_maximal_independent_sets: a CPLEX (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

from docplex.mp.model import Model


def create_model(instance):
    """Find a maximal independent set of a graph: a set of nodes, no two of them adjacent, that is not
    a subset of any other independent set."""
    neighbours = instance["adjacency_list"]  # neighbours[i]: the nodes, 1-based, adjacent to node i
    n = instance["n"]                        # the number of nodes

    model = Model("maximal_independent_sets")

    # nodes[i] is 1 when node i is in the independent set, and 0 when not
    nodes = model.binary_var_list(n, name="nodes")

    # Independence: no two adjacent nodes are both in the set.
    model.add_constraints(nodes[i] + nodes[k - 1] <= 1 for i in range(n) for k in neighbours[i])

    # Maximality: every node is in the set or has a neighbour in it, so no node can be added.
    model.add_constraints(nodes[i] + model.sum(nodes[k - 1] for k in neighbours[i]) >= 1
                          for i in range(n))

    return model, {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
