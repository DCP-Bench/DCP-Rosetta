# frog_circle: a PuLP (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python frog_circle.py frog_circle.json

import pulp


def create_model(instance):
    """Cards numbered 1 to n lie on a circle of n places. A frog starts on card 1 and, from
    each card k, jumps k places clockwise. Find an arrangement of the cards on which the
    frog lands on every card."""
    n_cards = instance["n"]  # the number of cards, which is also the number of places on the circle

    problem = pulp.LpProblem("frog_circle", pulp.LpMinimize)

    # put[p, k] is 1 when card k lies on place p, and 0 when not
    put = {(p, k): pulp.LpVariable(f"put_{p}_{k}", cat="Binary")
           for p in range(n_cards) for k in range(1, n_cards + 1)}
    # x[p] is the card on place p
    x = [pulp.LpVariable(f"x_{p}", 1, n_cards, cat="Integer") for p in range(n_cards)]
    # jump[p, q] is 1 when the frog's path of jumps goes from place p to place q, and 0 when not
    jump = {(p, q): pulp.LpVariable(f"jump_{p}_{q}", cat="Binary")
            for p in range(n_cards) for q in range(n_cards) if p != q}
    # visit[p] is the step at which the frog reaches place p, where place 0 is step 0
    visit = [pulp.LpVariable(f"visit_{p}", 0, n_cards - 1, cat="Integer") for p in range(n_cards)]

    # The card that takes the frog from place p to place q: the number of places clockwise from
    # p to q, where a full turn of the circle is card n.
    def jump_card(p, q):
        return (q - p) % n_cards or n_cards

    # Each place holds one card, and x[p] reads that card.
    for p in range(n_cards):
        problem += pulp.lpSum(put[p, k] for k in range(1, n_cards + 1)) == 1
        problem += x[p] == pulp.lpSum(k * put[p, k] for k in range(1, n_cards + 1))

    # Each card lies on one place.
    for k in range(1, n_cards + 1):
        problem += pulp.lpSum(put[p, k] for p in range(n_cards)) == 1

    # The frog starts on card 1, which lies on place 0.
    problem += put[0, 1] == 1

    # A jump from place p to place q is made from the card on place p, so that card must be the one that moves the frog from p to q.
    for (p, q), var in jump.items():
        problem += var <= put[p, jump_card(p, q)]

    # The frog leaves each place at most once and arrives at each place at most once.
    for p in range(n_cards):
        problem += pulp.lpSum(jump[p, q] for q in range(n_cards) if q != p) <= 1
        problem += pulp.lpSum(jump[q, p] for q in range(n_cards) if q != p) <= 1

    # No jump arrives at place 0, where the frog starts.
    problem += pulp.lpSum(jump[q, 0] for q in range(1, n_cards)) == 0

    # The frog's jumps form a path through all n places, with n - 1 jumps.
    problem += pulp.lpSum(jump.values()) == n_cards - 1

    # The frog is at place 0 at step 0, and every jump of the path reaches a later step, so the jumps cannot close into a loop.
    problem += visit[0] == 0
    for (p, q), var in jump.items():
        problem += visit[q] >= visit[p] + 1 - n_cards * (1 - var)

    return problem, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
