# frog_circle: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install ortools`):
#   python frog_circle.py frog_circle.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Cards numbered 1 to n are arranged in a circle. A frog starts on card 1 and,
    from card k, jumps k places clockwise. Find an arrangement of the cards that
    lets the frog land on every card."""
    n_cards = instance["n"]  # the number of cards, numbered 1 to n_cards

    model = cp_model.CpModel()

    # x[p] is the number of the card at position p of the circle
    x = [model.new_int_var(1, n_cards, f"x_{p}") for p in range(n_cards)]
    # pos[i] is the position on the circle where the frog is after its i-th jump (0 is the start)
    pos = [model.new_int_var(0, n_cards - 1, f"pos_{i}") for i in range(n_cards)]
    # visited[i] is the number of the card the frog is on after its i-th jump (0 is the start)
    visited = [model.new_int_var(1, n_cards, f"visited_{i}") for i in range(n_cards)]

    # The cards are all different, so are the positions the frog visits and the cards it lands on.
    model.add_all_different(x)
    model.add_all_different(pos)
    model.add_all_different(visited)

    # The frog starts on card 1, which sits at position 0.
    model.add(x[0] == 1)
    model.add(pos[0] == 0)
    model.add(visited[0] == 1)

    for i in range(1, n_cards):
        # the number on the card the frog jumps from
        here = model.new_int_var(1, n_cards, f"here_{i}")
        model.add_element(pos[i - 1], x, here)
        # Each jump goes clockwise by the number on the card the frog just left.
        target = model.new_int_var(0, 2 * n_cards, f"target_{i}")
        model.add(target == pos[i - 1] + here)
        model.add_modulo_equality(pos[i], target, n_cards)
        # The frog lands on the card at its new position.
        model.add_element(pos[i], x, visited[i])

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
