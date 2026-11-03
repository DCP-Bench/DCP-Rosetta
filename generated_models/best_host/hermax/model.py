# best_host: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install hermax`) with:
#   python best_host.py

from hermax.model import Model

# The statement fixes this data, so the instance carries nothing and create_model
# does not read its argument. Guests are numbered 0 Andrew, 1 Betty, 2 Cara,
# 3 Dave, 4 Erica, 5 Frank. WILLING_NEIGHBOURS[g] lists the guests g will sit next to.
WILLING_NEIGHBOURS = [[3, 5], [2, 4], [1, 5], [0, 4], [1, 3], [0, 2]]


def create_model(instance):
    """Seat the six guests around a round table so that every guest sits only next to
    guests they get along with. The statement's "minimize conflict" is posed here as
    finding a seating with no conflict at all (the satisfaction contract), so there is
    no objective. The output x lists the guests in seating order:
    x[i] is the guest in seat i, with the seats going round the table."""
    n = len(WILLING_NEIGHBOURS)  # the number of guests, which is also the number of seats
    m = Model()

    # x[i] is the guest seated in seat i (0 Andrew ... 5 Frank)
    x = m.int_vector("x", n, 0, n - 1)

    # Every guest has exactly one seat.
    m &= x.all_different()

    # A pair is compatible when each guest is willing to sit next to the other
    # (the filter changes nothing for this symmetric data).
    compatible = [(a, b) for a in range(n) for b in WILLING_NEIGHBOURS[a]
                  if a in WILLING_NEIGHBOURS[b]]

    # Each pair of neighbours at the table (seat n-1 is next to seat 0 again)
    # must be a compatible pair of guests.
    for i in range(n):
        m &= m.table([x[i], x[(i + 1) % n]], allowed=compatible)

    return m, {"x": x}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
