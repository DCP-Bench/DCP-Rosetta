# csplib_003_quasigroup_existence: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

from docplex.mp.model import Model


def create_model(instance):
    """Quasigroup existence (QG3): an order-m quasigroup, i.e. an m-by-m Latin square over 0..m-1
    read as a multiplication table, in which (a*b)*(b*a) = a for all elements a and b."""
    m = instance["m"]  # order of the quasigroup
    elems = range(m)

    model = Model("quasigroup_existence")
    # The QG3 rule below is a quadratic constraint over binaries, which is not convex; CPLEX
    # accepts it only when told to search for a global optimum.
    model.parameters.optimalitytarget = 3
    # Have CPLEX replace the products of binaries by linear constraints in presolve instead of
    # treating the constraints as general non-convex quadratic ones.
    model.parameters.preprocessing.qtolin = 1

    # is_[a, b, v] = 1 when a*b = v; every product has exactly one value.
    is_ = {(a, b, v): model.binary_var(name=f"is_{a}_{b}_{v}") for a in elems for b in elems for v in elems}
    model.add_constraints(model.sum(is_[a, b, v] for v in elems) == 1 for a in elems for b in elems)

    # Each element occurs once in every row.
    model.add_constraints(model.sum(is_[a, b, v] for b in elems) == 1 for a in elems for v in elems)

    # Each element occurs once in every column.
    model.add_constraints(model.sum(is_[a, b, v] for a in elems) == 1 for b in elems for v in elems)

    # QG3 property: (a*b)*(b*a) = a. Whenever a*b = u and b*a = w, then u*w = a. For fixed a and
    # u only one b has a*b = u (rows are Latin), so summing over b keeps the left side 0 or 1:
    # one quadratic constraint per (a, u, w), m^3 in all, instead of m^4 linear implications
    # that would exceed the Community Edition's 1000 constraints.
    for a in elems:
        for u in elems:
            for w in elems:
                model.add_constraint(model.sum(is_[a, b, u] * is_[b, a, w] for b in elems) <= is_[u, w, a])

    # quasigroup[a][b] is the product a * b, the multiplication table read from is_
    quasigroup = [[model.sum(v * is_[a, b, v] for v in elems) for b in elems] for a in elems]
    return model, {"quasigroup": quasigroup}


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
