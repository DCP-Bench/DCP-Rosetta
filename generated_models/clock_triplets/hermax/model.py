# clock_triplets: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install hermax`) with:
#   python clock_triplets.py

from hermax.model import Model


def create_model(instance):
    """Arrange the numbers 1 to 12 on the face of a clock, one number per position, so that
    no triplet of neighbouring numbers (three positions in a row, going round the clock)
    adds up to more than 21. The puzzle is fixed by its statement: the instance has no
    data, so its argument is not read."""
    n = 12  # the clock has 12 positions, and they hold the numbers 1 to 12

    m = Model()

    # x[i] is the number at position i of the clock, from 1 to 12
    x = m.int_vector("x", n, 1, n)

    # Every number from 1 to 12 appears exactly once on the clock.
    m &= x.all_different()

    # No three neighbouring positions add up to more than 21. The clock is a circle, so the
    # positions wrap around: after position 11 comes position 0, then position 1.
    for i in range(n):
        m &= (x[i] + x[(i + 1) % n] + x[(i + 2) % n] <= 21)

    return m, {"x": x}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
