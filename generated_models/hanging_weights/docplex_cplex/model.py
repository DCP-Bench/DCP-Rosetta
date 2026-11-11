# hanging_weights: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python hanging_weights.py

from docplex.mp.model import Model


def create_model(instance):
    """Hanging weights: thirteen weights A..M, all different integers from 1 to 13, hang from a
    system of bars; find them so that every bar balances about its pivot."""
    n_weights = 13  # the weights A..M
    names = "abcdefghijklm"
    values = range(1, n_weights + 1)  # the weights are different integers from 1 to 13

    model = Model("hanging_weights")

    # weighs[w, v] is 1 when weight w is v; each weight has one value and the weights are
    # all different.
    weighs = {(w, v): model.binary_var(name=f"{w}_is_{v}") for w in names for v in values}
    model.add_constraints(model.sum(weighs[w, v] for v in values) == 1 for w in names)
    model.add_constraints(model.sum(weighs[w, v] for w in names) <= 1 for v in values)
    # x[w] is the value of weight w
    x = {w: model.sum(v * weighs[w, v] for v in values) for w in names}
    a, b, c, d, e, f, g, h, i, j, k, l, m = (x[w] for w in names)

    # Each bar balances: the weights on either side of the pivot, times their distances,
    # are equal; a bar hanging beneath another counts as a single weight of its total.
    model.add_constraint(4 * a == b)                      # bar A-B
    model.add_constraint(5 * c == d)                      # bar C-D
    model.add_constraint(3 * e == 2 * f)                  # bar E-F
    model.add_constraint(3 * g == 2 * (c + d))            # bar G and the C-D bar
    model.add_constraint(3 * (a + b) + 2 * j == k + 2 * (g + c + d))   # bar J-K
    model.add_constraint(3 * h == 2 * (e + f) + 3 * i)    # bar H-I
    model.add_constraint(h + i + e + f == l + 4 * m)      # bar L-M
    model.add_constraint(4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d))  # top

    return model, dict(x)


if __name__ == "__main__":
    model, outputs = create_model({})
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
