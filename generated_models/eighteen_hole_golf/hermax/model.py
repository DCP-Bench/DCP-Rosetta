# eighteen_hole_golf: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install hermax`) with:
#   python eighteen_hole_golf.py

from hermax.model import Model


def create_model(instance):
    """Lay out a golf course of 18 holes, each of length (par) 3, 4 or 5, such that the
    total length of the course is 72. This is a satisfaction problem: any layout that
    meets the rules is an answer."""
    # The problem fixes the course: 18 holes, each of par 3 to 5, a total of 72.
    # The instance carries no data, so nothing is read from it.
    num_holes = 18
    shortest, longest = 3, 5
    total_length = 72

    m = Model()

    # holes[i] is the length of hole i, one of 3, 4 or 5
    holes = m.int_vector("holes", num_holes, shortest, longest)

    # The lengths of all the holes add up to the total length of the course.
    m &= (sum(holes[i] for i in range(num_holes)) == total_length)

    # The output: the length of each hole, in order.
    return m, {"holes": holes}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
