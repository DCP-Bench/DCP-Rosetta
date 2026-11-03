# frog_circle: a hermax (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install hermax`):
#   python frog_circle.py frog_circle.json

from hermax.model import Model


def create_model(instance):
    """Cards numbered 1 to n sit in a circle. A frog starts on card 1 and jumps
    clockwise by the number on the card it is on, forever. Find an arrangement of
    the cards so that the frog lands on every card."""
    n = instance["n"]  # n: the number of cards in the circle

    m = Model()

    # x[p] is the card at circle position p (0-based); the cards are 1..n.
    x = m.int_vector("x", n, 1, n)
    # Each card appears exactly once in the circle.
    m &= x.all_different()
    # Rotating the circle gives another valid arrangement, so card 1 is fixed at
    # position 0 as the representative of its rotation class (the fixed first
    # element of a rotation-invariant arrangement).
    m &= (x[0] == 1)

    # nxt[p] is the position the frog jumps to from position p: p + x[p],
    # wrapped back into the circle. wrap[p] is 1 exactly when that jump runs past
    # the last position, so nxt[p] = p + x[p] - n * wrap[p] stays in 0..n-1.
    nxt = m.int_vector("nxt", n, 0, n - 1)
    wrap = m.bool_vector("wrap", n)
    for p in range(n):
        m &= (nxt[p] == p + x[p] - n * wrap[p])

    # visit[t] is the position the frog is on after t jumps; it starts on card 1 at position 0.
    visit = m.int_vector("visit", n, 0, n - 1)
    m &= (visit[0] == 0)
    # Each jump moves the frog from its current position to the next one.
    for t in range(n - 1):
        m &= (nxt[visit[t]] == visit[t + 1])
    # The frog must land on every card: its first n positions are all different,
    # so they cover the whole circle.
    m &= visit.all_different()

    return m, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
