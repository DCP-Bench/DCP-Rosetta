# frog_circle: a Choco-solver (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python frog_circle.py frog_circle.json

from pychoco.model import Model


def create_model(instance):
    """Cards numbered 1 to n are arranged in a circle. A frog starts on card 1 and,
    from card k, jumps k places clockwise. Find an arrangement of the cards that
    lets the frog land on every card."""
    n_cards = instance["n"]  # the number of cards, numbered 1 to n_cards

    model = Model()

    # x[p] is the number of the card at position p of the circle, counting clockwise from
    # position 0; the card at position 0 is card 1, where the frog starts
    x = [model.intvar(1, 1 if p == 0 else n_cards, name=f"x_{p}") for p in range(n_cards)]
    # pos[i] is the position on the circle where the frog is after its i-th jump (0 is the start)
    pos = [model.intvar(0, 0 if i == 0 else n_cards - 1, name=f"pos_{i}")
           for i in range(n_cards)]
    # visited[i] is the number of the card the frog is on after its i-th jump (0 is the start)
    visited = [model.intvar(1, 1 if i == 0 else n_cards, name=f"visited_{i}")
               for i in range(n_cards)]

    # The cards are all different, and the frog lands on every position and every card once.
    model.all_different(x).post()
    model.all_different(pos).post()
    model.all_different(visited).post()

    # Each jump goes clockwise by the number on the card the frog jumps from.
    for i in range(1, n_cards):
        # card_before is the number on the card the frog jumps from
        card_before = model.intvar(1, n_cards, name=f"card_before_{i}")
        model.element(card_before, x, pos[i - 1]).post()
        # jump_to is the position reached before wrapping around the circle
        jump_to = model.intvar(1, 2 * n_cards - 1, name=f"jump_to_{i}")
        model.arithm(pos[i - 1], "+", card_before, "=", jump_to).post()
        model.mod(jump_to, n_cards, pos[i]).post()
        # The frog lands on the card at its new position.
        model.element(visited[i], x, pos[i]).post()

    return model, {"x": x}, None


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
