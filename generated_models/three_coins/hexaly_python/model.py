"""Three coins: from the starting faces, flip one coin per move so that after the given number of moves all coins match."""
import hexaly.optimizer as hx


def build(instance):
    init, moves = instance["init"], instance["num_moves"]  # the starting faces (1 is tails) and the number of moves
    n = len(init)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # steps[t][i] = 1 if coin i shows tails after t moves (0 = heads); steps[0] is the starting position
    steps = [list(init)] + [[model.bool() for _ in range(n)] for _ in range(moves)]

    # Each move chooses one coin and flips it over: exactly one coin differs from the move before
    for t in range(moves):
        model.constraint(model.sum(steps[t + 1][i] != steps[t][i] for i in range(n)) == 1)
    # After the last move the coins show all heads or all tails
    for i in range(1, n):
        model.constraint(steps[moves][i] == steps[moves][0])

    return optimizer, {"steps": steps}
