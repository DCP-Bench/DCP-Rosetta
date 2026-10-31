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
    # Use integers 0 (heads) and 1 (tails)
    coin_state = m.int_matrix("coin_state", num_moves + 1, num_coins, 0, 1)

    # Initial state constraints
    for coin_idx in range(num_coins):
        m &= (coin_state[0][coin_idx] == init[coin_idx])

    # State update: XOR operation
    # state[move+1][coin] = state[move][coin] XOR steps[move][coin]
    # Which means: state[move+1][coin] = (state[move][coin] + steps[move][coin]) % 2
    # Or equivalently: state[move+1][coin] != state[move][coin] if steps[move][coin] else state[move+1][coin] == state[move][coin]
    for move in range(num_moves):
        for coin_idx in range(num_coins):
            # If we flip, new_state is opposite; if not, new_state is same
            # new_state = (old_state == 0 and flip) OR (old_state == 1 and not flip)
            # Actually: new_state = old_state XOR flip
            # In 0/1 terms: (old_state + flip) mod 2
            # hermax: use auxiliary variable
            flipped = m.bool(f"flipped_{move}_{coin_idx}")
            m &= (flipped == steps[move][coin_idx])
            # State change: if flipped, toggle; else keep same
            m &= ((flipped & (coin_state[move + 1][coin_idx] == (1 - coin_state[move][coin_idx]))) |
                  (~flipped & (coin_state[move + 1][coin_idx] == coin_state[move][coin_idx])))

    # Final state: all coins must be the same
    # Either all heads (0) or all tails (1)
    final_coins = [coin_state[num_moves][i] for i in range(num_coins)]

    # All same: all equal first coin
    m &= ((final_coins[0] == final_coins[1]) & (final_coins[1] == final_coins[2]))

    outputs = {
        "steps": steps,
    }

    return m, outputs
