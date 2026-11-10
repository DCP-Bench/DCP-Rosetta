"""Big Bang dice: five six-sided dice with faces 1..12 whose 'beats' relations match Rock-Paper-Scissors-Lizard-Spock."""
import hexaly.optimizer as hx

ROCK, PAPER, SCISSORS, LIZARD, SPOCK = range(5)
# (winner, loser) for the ten relationships of the problem statement
BEATS = [(ROCK, SCISSORS), (ROCK, LIZARD), (PAPER, ROCK), (PAPER, SPOCK), (SCISSORS, PAPER),
         (SCISSORS, LIZARD), (LIZARD, PAPER), (LIZARD, SPOCK), (SPOCK, ROCK), (SPOCK, SCISSORS)]
FACES = 6


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # dice[d][f] is face f of die d, between 1 and 12 as the statement fixes
    dice = [[model.int(1, 12) for _ in range(FACES)] for _ in range(5)]

    for winner, loser in BEATS:
        # A beats B when A shows the strictly larger face in more than half of the 36 pairs of faces
        wins = model.sum(dice[winner][a] > dice[loser][b] for a in range(FACES) for b in range(FACES))
        model.constraint(2 * wins > FACES * FACES)

    return optimizer, {"dice": dice}
