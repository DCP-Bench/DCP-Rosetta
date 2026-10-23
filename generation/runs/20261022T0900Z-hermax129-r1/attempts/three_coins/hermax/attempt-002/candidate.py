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

    # Simulate the state of each coin after each move using integer 0/1 variables
    # coin_state[move][coin] = state of coin after move (0 = heads, 1 = tails)
    coin_state = m.int_matrix("coin_state", num_moves + 1, num_coins, 0, 1)

    # Initial state
    for coin_idx in range(num_coins):
        m &= (coin_state[0][coin_idx] == init[coin_idx])

    # State update: flip or keep
    # For each move and coin, post constraints:
    # If steps[move][coin] is true, toggle the state; else keep same
    for move in range(num_moves):
        for coin_idx in range(num_coins):
            # Create constraint: if flip, new state is opposite; else same
            # Using implication: flip -> (new != old), not flip -> (new == old)

            # When flip is true, new_state must be 1 - old_state
            m &= (steps[move][coin_idx] | (coin_state[move + 1][coin_idx] == coin_state[move][coin_idx]))

            # When flip is false (~steps[move][coin_idx]), new_state must be old_state
            m &= (~steps[move][coin_idx] | (coin_state[move + 1][coin_idx] == (1 - coin_state[move][coin_idx])))

    # Final state: all coins must be the same
    # All equal to first coin's final state
    for coin_idx in range(1, num_coins):
        m &= (coin_state[num_moves][coin_idx] == coin_state[num_moves][0])

    outputs = {
        "steps": steps,
    }

    return m, outputs
