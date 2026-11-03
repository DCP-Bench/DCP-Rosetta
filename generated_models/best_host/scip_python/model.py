# best_host: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python best_host.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """Seat six dinner guests around a round table so that as few guests as
    possible who do not get along sit next to each other. Each guest will only
    sit next to the guests the statement lists for them. The answer is the
    seating order: x[p] is the guest in seat p, seats 0 to 5 going round the
    table, with seat 5 next to seat 0."""

    # The statement fixes all the data, so the instance has no fields to read.
    # Guests are numbered 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank.
    N = 6  # six guests and six seats, both from the statement

    # Who each guest will sit next to, straight from the statement.
    will_sit_next_to = {
        0: [3, 5],  # Andrew will only sit next to Dave and Frank
        1: [2, 4],  # Betty will only sit next to Cara and Erica
        2: [1, 5],  # Cara will only sit next to Betty and Frank
        3: [0, 4],  # Dave will only sit next to Andrew and Erica
        4: [1, 3],  # Erica will only sit next to Betty and Dave
        5: [0, 2],  # Frank will only sit next to Andrew and Cara
    }

    model = Model("best_host")

    # seat[p, g] is 1 when guest g sits in seat p, and 0 when not.
    # The table is a grid: one row per seat, one column per guest.
    seat = model.addMatrixVar((N, N), vtype="B", name="seat")

    # Every seat holds exactly one guest.
    model.addMatrixCons(seat.sum(axis=1) == 1)

    # Every guest sits in exactly one seat.
    model.addMatrixCons(seat.sum(axis=0) == 1)

    # Seating rule: whoever sits next to a guest must be someone that guest will
    # sit next to. Seat q is the seat next to seat p (clockwise), and seat 5 is
    # next to seat 0, which is why q wraps round with the modulo.
    for p in range(N):
        q = (p + 1) % N
        for g in range(N):
            # if guest g is in seat p, the guest in seat q is someone g will sit next to
            model.addCons(seat[p, g] <= quicksum(seat[q, h] for h in will_sit_next_to[g]))
            # and the other way round: if g is in seat q, the guest in seat p is someone g will sit next to
            model.addCons(seat[q, g] <= quicksum(seat[p, h] for h in will_sit_next_to[g]))

    # No objective: a seating with no conflict exists (for example Andrew, Dave,
    # Erica, Betty, Cara, Frank round the table), so the least possible conflict is
    # zero, and the model asks for a seating with no conflict.

    # x[p] is the guest in seat p: the guest number of whoever holds seat p.
    x = [quicksum(g * seat[p, g] for g in range(N)) for p in range(N)]

    return model, {"x": x}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
