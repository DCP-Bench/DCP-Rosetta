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

    # State update: handle XOR without multiplication
    # For each move and coin, create four cases:
    # Case 1: old_state = 0, flip = 0 => new_state = 0
    # Case 2: old_state = 0, flip = 1 => new_state = 1
    # Case 3: old_state = 1, flip = 0 => new_state = 1
    # Case 4: old_state = 1, flip = 1 => new_state = 0

    for move in range(num_moves):
        for coin_idx in range(num_coins):
            old_state = coin_state[move][coin_idx]
            new_state = coin_state[move + 1][coin_idx]
            flip = steps[move][coin_idx]

            # Case analysis: use conditionals
            # If old_state == 0, then new_state == flip
            # If old_state == 1, then new_state == ~flip (i.e., 1 - flip)

            # Create auxiliary variables for the two cases
            is_old_zero = m.bool(f"is_old_zero_{move}_{coin_idx}")
            is_old_one = m.bool(f"is_old_one_{move}_{coin_idx}")

            # is_old_zero iff old_state == 0
            m &= (is_old_zero == (old_state == 0))
            m &= (is_old_one == (old_state == 1))

            # One of them must be true
            m &= (is_old_zero | is_old_one)

            # Now post constraints based on which case applies
            # If is_old_zero and flip, then new_state == 1
            # If is_old_zero and not flip, then new_state == 0
            # If is_old_one and flip, then new_state == 0
            # If is_old_one and not flip, then new_state == 1

            # Simplify: when old_state == 0, new_state == flip
            #           when old_state == 1, new_state == ~flip == (1 - flip) for 0/1 values

            # Using: new_state == (old_state == 0) ? flip : (1 - flip)
            # Create: (is_old_zero & flip & (new_state == 1)) |
            #         (is_old_zero & ~flip & (new_state == 0)) |
            #         (is_old_one & flip & (new_state == 0)) |
            #         (is_old_one & ~flip & (new_state == 1))

            # Check if new_state matches the XOR result
            # Create boolean variable for whether new_state is correct
            new_state_correct = m.bool(f"new_state_correct_{move}_{coin_idx}")

            # new_state_correct iff new_state == (old_state XOR flip)
            # Equivalently: new_state_correct iff (new_state + old_state + flip) mod 2 == 1
            # Or: (new_state + old_state + flip == 1) or (new_state + old_state + flip == 3)
            m &= (new_state_correct == ((new_state + old_state + flip == 1) | (new_state + old_state + flip == 3)))

            # This state must be correct
            m &= new_state_correct

    # Final state: all coins must be the same
    for coin_idx in range(1, num_coins):
        m &= (coin_state[num_moves][coin_idx] == coin_state[num_moves][0])

    outputs = {
        "steps": steps,
    }

    return m, outputs
