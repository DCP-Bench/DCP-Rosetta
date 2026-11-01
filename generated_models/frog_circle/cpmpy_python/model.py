# frog_circle: a CPMpy model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python frog_circle.py frog_circle.json

import cpmpy as cp


def create_model(instance):
    """Cards numbered 1 to n are arranged in a circle. A frog starts on card 1 and,
    from card k, jumps k places clockwise. Find an arrangement of the cards that
    lets the frog land on every card."""
    n = instance["n"]  # the number of cards, numbered 1 to n

    # x[p] is the number of the card at position p of the circle
    x = cp.intvar(1, n, shape=n, name="x")
    # pos[i] is the position of the circle where the frog lands on its i-th jump (0 is the start)
    pos = cp.intvar(0, n - 1, shape=n, name="pos")
    # visited[i] is the number of the card the frog lands on at its i-th jump
    visited = cp.intvar(1, n, shape=n, name="visited")

    model = cp.Model()
    # The cards are all different, so are the positions the frog visits and the cards it lands on.
    model.add(cp.AllDifferent(x))
    model.add(cp.AllDifferent(pos))
    model.add(cp.AllDifferent(visited))

    # The frog starts on card 1, which sits at position 0.
    model.add(x[0] == 1)
    model.add(pos[0] == 0)
    model.add(visited[0] == 1)

    for i in range(1, n):
        # Each jump goes clockwise by the number on the card the frog just left.
        model.add(pos[i] == (pos[i - 1] + x[pos[i - 1]]) % n)
        # The frog lands on the card at its new position.
        model.add(visited[i] == x[pos[i]])

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
