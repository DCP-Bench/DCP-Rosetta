# frog_circle: a CPLEX (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python frog_circle.py frog_circle.json

from docplex.mp.model import Model


def create_model(instance):
    """Frog circle: lay the cards 1..n face up at n positions around a circle. A frog starts on
    card 1 at position 0 and repeatedly jumps clockwise as many positions as the card it sits on
    shows. Arrange the cards so that the frog lands on every position exactly once in n - 1 jumps."""
    n = instance["n"]  # number of cards and positions
    positions = range(n)
    steps = range(n)
    cards = range(1, n + 1)

    model = Model("frog_circle")

    # card_at[p, c] is 1 when card c lies at position p. Every position holds one card and every
    # card lies at one position, so the cards are all different.
    card_at = {(p, c): model.binary_var(name=f"card_at_{p}_{c}") for p in positions for c in cards}
    model.add_constraints(model.sum(card_at[p, c] for c in cards) == 1 for p in positions)
    model.add_constraints(model.sum(card_at[p, c] for p in positions) == 1 for c in cards)
    # x[p] is the card at position p.
    x = [model.sum(c * card_at[p, c] for c in cards) for p in positions]

    # visits[i, p] is 1 when the frog is at position p after i jumps. It is at one position at
    # each step and visits every position once, so the positions are all different.
    visits = {(i, p): model.binary_var(name=f"visits_{i}_{p}") for i in steps for p in positions}
    model.add_constraints(model.sum(visits[i, p] for p in positions) == 1 for i in steps)
    model.add_constraints(model.sum(visits[i, p] for i in steps) == 1 for p in positions)
    # pos[i] is the position of the frog after i jumps
    pos = [model.sum(p * visits[i, p] for p in positions) for i in steps]

    # visited[i] is the card the frog sits on after i jumps: the card at position pos[i]. One
    # indicator per step and position copies the card at the frog's position.
    visited = [model.integer_var(1, n, name=f"visited_{i}") for i in steps]
    for i in steps:
        for p in positions:
            model.add_indicator(visits[i, p], visited[i] == x[p])

    # The frog starts on card 1. Positions are counted from the frog's start, so card 1 lies at
    # position 0 (this fixes the rotation of the circle: the printed arrangement starts at card 1).
    model.add_constraint(x[0] == 1)
    model.add_constraint(pos[0] == 0)

    # The next position is the previous position plus the card there, modulo n. The sum is
    # below 2 * n, so wraps[i] (0 or 1) says whether the jump passes position 0.
    for i in range(1, n):
        wraps = model.binary_var(name=f"wraps_{i}")
        model.add_constraint(pos[i] == pos[i - 1] + visited[i - 1] - n * wraps)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
