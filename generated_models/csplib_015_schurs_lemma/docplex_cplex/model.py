# csplib_015_schurs_lemma: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

from docplex.mp.model import Model


def create_model(instance):
    """Schur's lemma: put balls 1..n into c boxes so that no x + y = z triple lies entirely in one box."""
    n = instance["n"]  # the number of balls, labelled 1 .. n
    c = instance["c"]  # the number of boxes, labelled 1 .. c
    balls = range(1, n + 1)
    boxes = range(1, c + 1)

    model = Model("schurs_lemma")

    # inbox[i, j] is 1 when ball i is in box j, and 0 when not
    inbox = model.binary_var_matrix(balls, boxes, name="inbox")

    # Every ball is in exactly one box.
    model.add_constraints(model.sum(inbox[i, j] for j in boxes) == 1 for i in balls)

    # For every x + y = z, with x <= y, the three balls are not all in the same box. When
    # x == y the ball is counted twice, so x and z may not share a box.
    model.add_constraints(inbox[x, j] + inbox[y, j] + inbox[x + y, j] <= 2
                          for x in balls for y in range(x, n - x + 1) for j in boxes)

    # The box of each ball, read back from the assignment.
    return model, {"balls": [model.sum(j * inbox[i, j] for j in boxes) for i in balls]}


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
