# five_brigands: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python five_brigands.py

from docplex.mp.model import Model


def create_model(instance):
    """Five brigands, Alfonso (A), Benito (B), Carlos (C), Diego (D) and Esteban (E), have
    captured 200 doubloons in all. Had Alfonso twelve times as much, Benito three times, Carlos
    the same, Diego half and Esteban a third, they would still have 200 in all. How many
    doubloons has each, if no brigand has less than one?"""
    total = 200  # the doubloons captured, and the total again after the changes
    model = Model("five_brigands")
    names = ["A", "B", "C", "D", "E"]

    # share[x] is the number of doubloons of brigand x: at least one, and at most the total
    share = {x: model.integer_var(1, total, name=x) for x in names}
    A, B, C, D, E = (share[x] for x in names)

    # Altogether they captured exactly 200 doubloons.
    model.add_constraint(A + B + C + D + E == total)
    # With twelve times as much for A, three times for B, the same for C, half for D and a third
    # for E the total is still 200: 12 A + 3 B + C + D / 2 + E / 3 = 200, times 6 to keep integers.
    model.add_constraint(6 * (12 * A + 3 * B + C) + 3 * D + 2 * E == 6 * total)

    return model, dict(share)


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
