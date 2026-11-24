# pythagorean_triplet: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python pythagorean_triplet.py

from docplex.mp.model import Model


def create_model(instance):
    """Find the Pythagorean triplet, three natural numbers a, b and c with a^2 + b^2 = c^2,
    for which a + b + c = 1000."""
    total = 1000  # the required sum a + b + c
    # Natural numbers start at 1. None is above 500: c^2 = a^2 + b^2 < (a + b)^2 gives c < a + b,
    # so 2 * c < 1000, and a and b are smaller than c. No triplet is cut off.
    top = 500

    model = Model("pythagorean_triplet")
    # Exact integers: the linearised products below are only right when every bit is exactly 0 or 1.
    model.parameters.mip.tolerances.integrality = 0

    # the three numbers of the triplet
    a = model.integer_var(1, top, name="a")
    b = model.integer_var(1, top, name="b")
    c = model.integer_var(1, top, name="c")

    # The three numbers add up to 1000.
    model.add_constraint(a + b + c == total)

    # a^2 + b^2 = c^2. CPLEX refuses this non-convex quadratic equality. With
    # c = 1000 - a - b it is the same as a^2 + b^2 = (1000 - a - b)^2, which simplifies to
    # a * b = 1000 * a + 1000 * b - 500000, so only the product a * b is needed. It is
    # written through the binary digits of a: a = sum 2^i bit_i and
    # a * b = sum 2^i (bit_i * b), each bit_i * b a binary times an integer in 0..500.
    # bit[i] is the i-th binary digit of a; width digits cover every value up to top
    width = top.bit_length()
    bit = [model.binary_var(name=f"a_bit_{i}") for i in range(width)]
    model.add_constraint(a == model.sum(2 ** i * bit[i] for i in range(width)))
    partial = []
    for i in range(width):
        # p is bit[i] * b, kept exact by the three rows below
        p = model.integer_var(0, top, name=f"b_times_bit_{i}")
        model.add_constraint(p <= top * bit[i])
        model.add_constraint(p <= b)
        model.add_constraint(p >= b - top * (1 - bit[i]))
        partial.append(2 ** i * p)
    model.add_constraint(2 * model.sum(partial) == 2 * total * a + 2 * total * b - total * total)

    return model, {"a": a, "b": b, "c": c}


if __name__ == "__main__":
    model, outputs = create_model({})
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
