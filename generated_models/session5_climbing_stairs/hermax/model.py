# session5_climbing_stairs: a hermax (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install hermax`):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

from hermax.model import Model


def create_model(instance):
    """Climb a stair of n steps, taking between m1 and m2 steps at each move. Give the
    number of steps taken at each of n moves: each is either 0 (no move, once the top
    is reached) or between m1 and m2, the steps taken add up to exactly n, and the
    moves that take no steps come last. This is a satisfaction problem: no objective."""
    n = instance["n"]     # the number of steps in the stair
    m1 = instance["m1"]   # the fewest steps allowed in one move
    m2 = instance["m2"]   # the most steps allowed in one move

    m = Model()

    # steps[i] is the number of steps taken at move i: 0 once the top is reached, otherwise
    # between m1 and m2. At most n moves are needed (one step each), so there are n moves.
    steps = m.int_vector("steps", n, 0, m2)

    # The moves together climb exactly the whole stair.
    m &= (sum(steps[i] for i in range(n)) == n)

    # Each move takes either no steps, or at least m1 steps.
    for i in range(n):
        m &= ((steps[i] == 0) | (steps[i] >= m1))

    # Moves that take no steps come last: once a move takes none, every later move takes none.
    for i in range(1, n):
        m &= ((steps[i] == 0) | (steps[i - 1] >= 1))

    return m, {"steps": steps}


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
