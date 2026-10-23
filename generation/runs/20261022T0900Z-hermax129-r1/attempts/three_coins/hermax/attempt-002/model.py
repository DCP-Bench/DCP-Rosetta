"""Three Coins - flip coins to make them all the same in exactly 3 moves.

Initial state: tails, heads, tails (1, 0, 1).
Goal: make all coins show the same face (all heads or all tails).
"""

from hermax.model import Model


def build(instance):
    num_moves = instance["num_moves"]
    init = instance["init"]
    num_coins = len(init)

    m = Model()

    # steps[move][coin] = True if we flip that coin in that move
    steps = m.bool_matrix("steps", num_moves, num_coins)

    # Simulate the state of each coin after each move
    # coin_state[move][coin] = state of coin after move (0 = heads, 1 = tails)
    coin_state = m.int_matrix("coin_state", num_moves + 1, num_coins, 0, 1)

    # Initial state
    for coin_idx in range(num_coins):
        m &= (coin_state[0][coin_idx] == init[coin_idx])

    # State update: enumerate all possible flip combinations and their results
    # For each move, determine the new state based on whether coins are flipped
    for move in range(num_moves):
        for coin_idx in range(num_coins):
            # If we flip, new state is 1-old; else new state is old
            # Express as: new_state = old_state + steps[coin] - 2 * old_state * steps[coin] (mod 2)
            # Simplify: new_state = old_state XOR steps[coin]

            # Direct constraint:
            # new_state = (old_state == 0 and steps) or (old_state == 1 and not steps)
            # Which is: (old_state + steps) mod 2 = new_state
            # In integer form: new_state = 1 - old_state if steps else old_state

            old_state = coin_state[move][coin_idx]
            new_state = coin_state[move + 1][coin_idx]
            flip = steps[move][coin_idx]

            # Create conditional: if flip then new_state != old_state else new_state == old_state
            # Post two linear constraints:
            # (1) if flip is true: new_state + old_state == 1
            # (2) if flip is false: new_state == old_state
            # Using big-M formulation with flip as selector:
            # new_state + old_state == 1 + 2*(1-flip) => satisfied when flip=true, not enforced when flip=false
            # new_state == old_state + 2*flip - 1 => new_state = old_state when flip=false

            # Simpler: use sum constraints
            # new_state = old_state if not flip, new_state = 1-old_state if flip
            # Combine: new_state == old_state + flip - 2*old_state*flip (this is XOR)

            # Use integer arithmetic: (old + flip) mod 2 = new
            # Without mod: old + flip - 2*old*flip == new (works for 0/1 values)
            m &= (new_state == (old_state + flip - 2 * old_state * flip))

    # Final state: all coins must be the same
    for coin_idx in range(1, num_coins):
        m &= (coin_state[num_moves][coin_idx] == coin_state[num_moves][0])

    outputs = {
        "steps": steps,
    }

    return m, outputs
