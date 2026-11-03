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
    # Bounds: a < b < c and a + b + c = 1000, so a < 1000 / 3, b < 500 and c > 1000 / 3.
    a = m.int("a", 1, 332)    # the shortest side
    b = m.int("b", 2, 499)    # the middle side
    c = m.int("c", 334, 997)  # the longest side, the hypotenuse

    # The sides are in order: a < b < c.
    m &= (a + 1 <= b)
    m &= (b + 1 <= c)

    # The perimeter is 1000: a + b + c = 1000.
    m &= (a + b + c == TOTAL)

    # Pythagoras: a^2 + b^2 = c^2. hermax has no product of two variables, so the equation
    # is rewritten. With c = 1000 - a - b, a^2 + b^2 = c^2 becomes
    # a*b - 1000*a - 1000*b + 500000 = 0, i.e. b * (1000 - a) = 500000 - 1000*a.
    # For each value k of a this is a linear equation in b alone, which holds only when a == k.
    for k in range(a.lb, a.ub + 1):
        m &= (b * (TOTAL - k) == 500000 - TOTAL * k).only_if(a == k)

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
