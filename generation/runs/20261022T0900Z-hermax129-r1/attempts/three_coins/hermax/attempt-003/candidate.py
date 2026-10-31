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

    # State update: XOR operation via linear constraint
    # new_state = old_state XOR flip
    # In integer form (works for 0/1 values): new_state == old_state + flip - 2*old_state*flip
    for move in range(num_moves):
        for coin_idx in range(num_coins):
            old_state = coin_state[move][coin_idx]
            new_state = coin_state[move + 1][coin_idx]
            flip = steps[move][coin_idx]

            # XOR constraint: (old + flip) mod 2 = new
            # Linear form: old + flip - 2*old*flip == new
            m &= (new_state == (old_state + flip - 2 * old_state * flip))

    # Final state: all coins must be the same
    for coin_idx in range(1, num_coins):
        m &= (coin_state[num_moves][coin_idx] == coin_state[num_moves][0])

    outputs = {
        "steps": steps,
    }

    return m, outputs
