# frog_circle: a PyCSP3 model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python frog_circle.py frog_circle.json

from pycsp3 import *


def create_model(instance):
    """Cards numbered 1 to n are arranged in a circle. A frog jumps on card 1, then one place
    clockwise, and from card k it jumps k places clockwise, and so on forever. Find an
    arrangement of the cards such that the frog jumps on every card, starting from card 1."""
    n_cards = instance["n"]  # the number of cards, which is also the number of places on the circle

    # x[p] is the card at place p of the circle, places numbered 0 to n_cards - 1 clockwise
    x = VarArray(size=n_cards, dom=range(1, n_cards + 1))

    # visit[t] is the place the frog is on after t jumps, the frog starting at place 0
    visit = VarArray(size=n_cards, dom=range(n_cards))

    satisfy(
        # The cards are numbered 1 to n_cards, each used once.
        AllDifferent(x),
        # Card 1 is at place 0: rotations of a solution are also solutions; only the one with card 1 at place 0 is kept.
        x[0] == 1,
        # The frog starts at place 0.
        visit[0] == 0,
    )

    satisfy(
        # The frog lands on n_cards different places, so it jumps on every card; it need not come back to card 1 (the description asks only that every card is visited).
        AllDifferent(visit),
    )

    satisfy(
        # From place visit[t] the frog jumps x[visit[t]] places clockwise around the circle of n_cards places.
        visit[t + 1] == (visit[t] + x[visit[t]]) % n_cards for t in range(n_cards - 1)
    )

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
