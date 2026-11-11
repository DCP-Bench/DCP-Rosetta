# session5_climbing_stairs: a CPLEX (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

from docplex.mp.model import Model


def create_model(instance):
    """Climbing stairs: climb n steps in moves of m1 to m2 steps each, padding with zero moves once at the top."""
    n = instance["n"]      # the number of steps of the stair
    m1 = instance["m1"]    # the fewest steps a move can take
    m2 = instance["m2"]    # the most steps a move can take
    # There are at most n moves (that many when every move takes one step), so n moves are
    # listed and the unused ones at the end take 0 steps.

    model = Model("climbing_stairs")

    # steps[i] is the number of steps taken at move i: 0 once the top is reached, else m1..m2.
    steps = model.integer_var_list(n, 0, m2, name="steps")
    # moving[i] is 1 exactly when move i takes at least one step.
    moving = model.binary_var_list(n, name="moving")

    # The moves climb the whole stair.
    model.add_constraint(model.sum(steps) == n, ctname="total")

    # A move that is taken covers m1 to m2 steps (and at least one, so that
    # moving[i] is 1 only for a real move); a move not taken covers none.
    model.add_constraints(steps[i] >= max(m1, 1) * moving[i] for i in range(n))
    model.add_constraints(steps[i] <= m2 * moving[i] for i in range(n))

    # Once a move is zero, every later move is zero too: no steps are taken after the top.
    model.add_constraints(moving[i] <= moving[i - 1] for i in range(1, n))

    return model, {"steps": steps}


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
