# broken_weights: a CPLEX (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python broken_weights.py broken_weights.json

from docplex.mp.model import Model


def create_model(instance):
    """Broken weights: a measuring weight of m pounds broke into n pieces of whole-pound weights.
    On a balance scale each piece goes on the object's side, on the other side, or stays off; the
    pieces must be able to weigh every whole weight from 1 to m. What do the pieces weigh?"""
    m = instance["m"]  # total weight of the pieces
    n = instance["n"]  # number of pieces

    pieces = range(n)
    values = range(1, m + 1)

    model = Model("broken_weights")

    # weighs[j, v] is 1 when piece j weighs v pounds, v in 1..m; each piece has one weight.
    weighs = {(j, v): model.binary_var(name=f"weighs_{j}_{v}") for j in pieces for v in values}
    model.add_constraints(model.sum(weighs[j, v] for v in values) == 1 for j in pieces)

    # weights[j] is the weight of piece j.
    weights = [model.sum(v * weighs[j, v] for v in values) for j in pieces]

    # The pieces add up to the total weight.
    model.add_constraint(model.sum(weights) == m)

    # Every load from 1 to m can be weighed. Stating a side (-1, 0, 1) for every piece and
    # load multiplies two variables, so the model uses an equivalent condition on the weights
    # instead. Take the pieces from lightest to heaviest, and let S be the total of the pieces
    # lighter than the next one, w. Every load from 1 to m can be weighed exactly when each
    # w is at most 2 * S + 1 (so the lightest piece weighs 1):
    # - enough: if the lighter pieces weigh every load from -S to S, adding w on either side or
    #   leaving it off covers every load from -(S + w) to S + w, since w - S <= S + 1;
    # - needed: if w >= 2 * S + 2, every piece from w up weighs more than S + 1, so the load
    #   m - S - 1 needs all of them on the other side, and the lighter pieces would then have
    #   to make up S + 1 > S.
    # Pieces of equal weight meet the condition once the first of them does, so it is stated
    # once per weight value v that some piece takes: v <= 2 * (total of pieces lighter than v)
    # + 1. The pieces themselves are not put in order; the condition is on the multiset.
    # used[v] is 1 when some piece weighs v.
    used = {v: model.binary_var(name=f"used_{v}") for v in values}
    for v in values:
        count = model.sum(weighs[j, v] for j in pieces)
        lighter = model.sum(u * weighs[j, u] for j in pieces for u in range(1, v))
        model.add_constraint(count <= n * used[v])
        model.add_constraint(v * used[v] <= 2 * lighter + 1)

    return model, {"weights": weights}


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
