# packing_rectangles: a Choco-solver (Python) model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python packing_rectangles.py packing_rectangles.json

from pychoco.model import Model


def create_model(instance):
    """Rectangle packing: place rectangular items of given widths and heights, without
    rotation and without overlap, inside a bounding rectangle of the smallest possible area."""
    widths = instance["widths"]    # widths[i]: the width of item i
    heights = instance["heights"]  # heights[i]: the height of item i
    n_items = len(widths)

    # The bounding rectangle is at least as wide as the widest item and at most as wide as
    # all items side by side; the same holds for its height.
    min_x, max_x = max(widths), sum(widths)
    min_y, max_y = max(heights), sum(heights)

    model = Model()

    # pos_x[i], pos_y[i]: the position of the lower-left corner of item i, measured from the
    # left and bottom edges of the bounding rectangle
    pos_x = [model.intvar(0, max_x, name=f"pos_x_{i}") for i in range(n_items)]
    pos_y = [model.intvar(0, max_y, name=f"pos_y_{i}") for i in range(n_items)]

    # total_x, total_y: the width and the height of the bounding rectangle
    total_x = model.intvar(min_x, max_x, name="total_x")
    total_y = model.intvar(min_y, max_y, name="total_y")

    # Every item lies inside the bounding rectangle.
    for i in range(n_items):
        model.arithm(pos_x[i], "-", total_x, "<=", -widths[i]).post()
        model.arithm(pos_y[i], "-", total_y, "<=", -heights[i]).post()

    # item_widths[i], item_heights[i]: the fixed size of item i
    item_widths = [model.intvar(w, w) for w in widths]
    item_heights = [model.intvar(h, h) for h in heights]

    # No two items overlap: each pair has one item entirely left of, right of, above or below the other.
    model.diff_n(pos_x, pos_y, item_widths, item_heights, True).post()

    # area: the area of the bounding rectangle, at least the total area of the items.
    area = model.intvar(sum(w * h for w, h in zip(widths, heights)), max_x * max_y, name="area")
    model.times(total_x, total_y, area).post()

    # Minimise the area of the bounding rectangle.
    return model, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}, {"objective": area, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
