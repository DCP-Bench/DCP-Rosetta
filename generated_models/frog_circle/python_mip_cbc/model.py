# frog_circle: a Python-MIP (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python frog_circle.py frog_circle.json

import mip


def create_model(instance):
    """Cards numbered 1 to n are arranged in a circle. A frog starts on card 1 and, from each card k,
    jumps k places clockwise. Find an arrangement of the cards that lets the frog land on every card."""
    n = instance["n"]  # the number of cards, numbered 1 to n

    model = mip.Model(solver_name="CBC")

    # x[p] is the card at position p. Positions 0 to n-1 are the places around the circle,
    # counted clockwise from the start. Card 1 is at position 0, where the frog starts;
    # turning the circle gives the same walk, so this is no restriction.
    x = [model.add_var(f"x_{p}", lb=1, ub=(1 if p == 0 else n), var_type=mip.INTEGER)
         for p in range(n)]

    # jump[p, d] is 1 when the frog jumps from position p by d places, for d from 1 to n-1.
    # Only jumps that do not land on the start are considered.
    jump = {}
    for p in range(n):
        for d in range(1, n):
            if (p + d) % n != 0:
                jump[p, d] = model.add_var(f"jump_{p}_{d}", var_type=mip.BINARY)

    # outgoing[p] lists the jumps from position p, and incoming[q] lists the jumps that land on position q.
    outgoing = {p: [] for p in range(n)}
    incoming = {q: [] for q in range(n)}
    for (p, d) in jump:
        outgoing[p].append((p, d))
        incoming[(p + d) % n].append((p, d))

    # The frog jumps from each position at most once.
    for p in range(n):
        model += mip.xsum(jump[pd] for pd in outgoing[p]) <= 1

    # The frog lands on every position except the start, and on each one once.
    for q in range(1, n):
        model += mip.xsum(jump[pd] for pd in incoming[q]) == 1

    # Each jump length from 1 to n-1 is used by exactly one jump, since the cards 1 to n-1
    # are the jump lengths, each used once.
    for d in range(1, n):
        model += mip.xsum(jump[p, d] for p in range(n) if (p, d) in jump) == 1

    # The card at each position is the length of the jump from it. The last card the frog
    # lands on jumps n places back to the start, so it holds card n.
    for p in range(n):
        leaves = mip.xsum(jump[pd] for pd in outgoing[p])  # 1 when the frog jumps from p, 0 at the last card
        model += x[p] == mip.xsum(d * jump[p, d] for d in range(1, n) if (p, d) in jump) + n - n * leaves

    # flow[p, d] is the amount of flow carried by the jump from position p by d places.
    flow = {}
    for (p, d) in jump:
        flow[p, d] = model.add_var(f"flow_{p}_{d}", lb=0, ub=n - 1, var_type=mip.CONTINUOUS)
        model += flow[p, d] <= (n - 1) * jump[p, d]

    # The walk from the start cannot close a loop that misses the start: every position other than
    # the start takes in one more unit of flow than it passes on, and flow moves only along jumps the frog makes.
    for q in range(1, n):
        model += mip.xsum(flow[pd] for pd in incoming[q]) - mip.xsum(flow[pd] for pd in outgoing[q]) == 1

    return model, {"x": x}


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
