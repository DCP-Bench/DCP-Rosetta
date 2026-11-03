# pythagorean_triplet: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install hermax`) with:
#   python pythagorean_triplet.py

from hermax.model import Model

TOTAL = 1000  # the statement fixes a + b + c = 1000 (a constant of the problem, not of the instance)


def create_model(instance):
    """Find the Pythagorean triplet a < b < c of natural numbers with a^2 + b^2 = c^2 and
    a + b + c = 1000. The statement says exactly one such triplet exists. The instance
    carries no data (its file is empty), so every number comes from the statement."""
    m = Model()

    # a, b, c are the three sides, with a < b < c.
    # Bounds: a < b < c and a + b + c = TOTAL, so a < TOTAL / 3, b < TOTAL / 2 and c > TOTAL / 3.
    a = m.int("a", 1, (TOTAL - 3) // 3)    # the shortest side
    b = m.int("b", 2, (TOTAL - 2) // 2)    # the middle side
    c = m.int("c", TOTAL // 3 + 1, TOTAL - 3)  # the longest side, the hypotenuse

    # The sides are in order: a < b < c.
    m &= (a + 1 <= b)
    m &= (b + 1 <= c)

    # The perimeter is TOTAL: a + b + c = TOTAL.
    m &= (a + b + c == TOTAL)

    # Pythagoras: a^2 + b^2 = c^2. hermax has no product of two variables, so the equation
    # is rewritten. With c = TOTAL - a - b, a^2 + b^2 = c^2 becomes
    # a*b - TOTAL*a - TOTAL*b + TOTAL^2/2 = 0, i.e. b * (TOTAL - a) = TOTAL^2/2 - TOTAL*a.
    # For each value k of a this is a linear equation in b alone, which holds only when a == k.
    for k in range(a.lb, a.ub + 1):
        m &= (b * (TOTAL - k) == TOTAL * TOTAL // 2 - TOTAL * k).only_if(a == k)

    # No objective: the problem asks for a triplet that satisfies the constraints above.
    return m, {"a": a, "b": b, "c": c}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
