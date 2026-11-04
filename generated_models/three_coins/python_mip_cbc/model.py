# three_coins: a Python-MIP (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python three_coins.py three_coins.json

import mip


def create_model(instance):
    """Three coins lie on a table. In exactly the given number of moves, each move
    turning one coin over, make them all face either heads or tails."""
    init = instance["init"]           # init[i] is 1 when coin i starts tails up, 0 when heads
    n_moves = instance["num_moves"]   # the number of moves
    n_coins = len(init)               # the number of coins

    model = mip.Model(solver_name="CBC")

    # state[t][i] is 1 when coin i shows tails after t moves. The starting faces are fixed.
    state = [[model.add_var(f"state_0_{i}", var_type=mip.INTEGER, lb=init[i], ub=init[i])
              for i in range(n_coins)]]
    state += [[model.add_var(f"state_{t}_{i}", var_type=mip.BINARY)
               for i in range(n_coins)]
              for t in range(1, n_moves + 1)]

    # flip[t][i] is 1 when the move from state t to state t+1 turns coin i over
    flip = [[model.add_var(f"flip_{t}_{i}", var_type=mip.BINARY)
             for i in range(n_coins)]
            for t in range(n_moves)]

    # Each move turns exactly one coin over.
    for t in range(n_moves):
        model.add_constr(mip.xsum(flip[t]) == 1)

    # A coin shows the opposite face after a move when it is turned over, and keeps its face otherwise.
    for t in range(n_moves):
        for i in range(n_coins):
            before = state[t][i]
            after = state[t + 1][i]
            flipped = flip[t][i]
            model.add_constr(after <= before + flipped)
            model.add_constr(after >= before - flipped)
            model.add_constr(after >= flipped - before)
            model.add_constr(after <= 2 - before - flipped)

    # After the last move all coins face the same way.
    for i in range(1, n_coins):
        model.add_constr(state[n_moves][i] == state[n_moves][0])

    return model, {"steps": state}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
