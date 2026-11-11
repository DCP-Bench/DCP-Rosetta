# circular_table_averbach_1_2: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python circular_table_averbach_1_2.py

from docplex.mp.model import Model


def create_model(instance):
    """Averbach 1.2: three players X, Y, Z of nationalities American, English and French sit
    around a circular table, each passing three cards to the person on their right. Y passed
    three hearts to the American, and X passed the queen of spades and two diamonds to the person
    who passed their cards to the Frenchwoman. What is the nationality of each player?"""
    n = 3  # three players, three nationalities, three seats
    seats = range(n)

    model = Model("circular_table_averbach_1_2")

    def seat_variables(names):
        # The seat, 0, 1 or 2, of each of the three people called names; at[i, s] is 1 when
        # person i sits at seat s. Seat 1 is right of seat 0, seat 2 right of seat 1 and seat 0
        # right of seat 2. A player and a nationality with the same seat are the same person.
        at = {(i, s): model.binary_var(name=f"{names[i]}_at_{s}") for i in range(n) for s in seats}
        # Each person has one seat, and no two people share a seat.
        model.add_constraints(model.sum(at[i, s] for s in seats) == 1 for i in range(n))
        model.add_constraints(model.sum(at[i, s] for i in range(n)) == 1 for s in seats)
        seat = [model.integer_var(0, n - 1, name=names[i]) for i in range(n)]
        model.add_constraints(seat[i] == model.sum(s * at[i, s] for s in seats) for i in range(n))
        return seat

    x, y, z = seat_variables(["x", "y", "z"])
    american, english, french = seat_variables(["american", "english", "french"])

    def right_to(a, b, name):
        # a is right of b: a == (b + 1) mod 3. With b in 0..2, b + 1 is 1..3, so
        # a == b + 1 - 3 * wrap, where wrap is 1 only when b + 1 == 3.
        wrap = model.binary_var(name=name)
        model.add_constraint(a - b + n * wrap == 1)

    # Y passed three hearts to the American, so the American sits right of Y.
    right_to(american, y, "wrap_american")
    # X passed to the person who passed to the Frenchwoman, so X sits right of the Frenchwoman.
    right_to(x, french, "wrap_x")

    return model, {"x": x, "y": y, "z": z,
                   "american": american, "english": english, "french": french}


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
