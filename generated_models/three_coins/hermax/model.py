# three_coins: a hermax (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install hermax`):
#   python three_coins.py three_coins.json

from hermax.model import Model


def create_model(instance):
    """Three coins lie on a table, tails, heads, tails. In exactly num_moves moves, each
    move flipping one coin, make them all face heads or all face tails. Report the
    arrangement after every move, starting with the given one."""
    init = instance["init"]              # init[i]: 1 if coin i starts tails, 0 if heads
    num_moves = instance["num_moves"]    # the number of moves to make
    n = len(init)                        # the number of coins

    m = Model()

    # state[t][i] is True when coin i shows tails after t moves (row 0 is the start)
    state = m.bool_matrix("state", num_moves + 1, n)
    # flipped[t][i] is True when move t flips coin i
    flipped = m.bool_matrix("flipped", num_moves, n)

    # The start is the given arrangement.
    for i in range(n):
        m &= (state[0][i] if init[i] == 1 else ~state[0][i])

    # Each move flips exactly one coin. A coin is flipped by a move exactly when its face
    # differs between the state before and after the move (the two Booleans differ).
    for t in range(num_moves):
        m &= flipped[t].exactly_one()
        for i in range(n):
            m &= (state[t][i] + state[t + 1][i] == 1).iff(flipped[t][i])

    # The final arrangement shows all tails or all heads.
    last = state[num_moves]
    all_tails = m.bool()  # True when every coin shows tails at the end
    all_heads = m.bool()  # True when every coin shows heads at the end
    m &= (sum(last) == n).iff(all_tails)
    m &= (sum(last) == 0).iff(all_heads)
    m &= (all_tails | all_heads)

    return m, {"steps": state}


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
