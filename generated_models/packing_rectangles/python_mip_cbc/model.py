# packing_rectangles: a Python-MIP (Python) model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python packing_rectangles.py packing_rectangles.json

import mip


def create_model(instance):
    """Rectangle packing: place rectangles of given widths and heights inside a container,
    without rotating them and without overlap, so that the container has the smallest
    possible area."""
    widths = instance["widths"]    # widths[i]: the width of rectangle i
    heights = instance["heights"]  # heights[i]: the height of rectangle i
    n_rects = len(widths)          # the number of rectangles

    # Sums and maxima of the sides: the container is never longer than all rectangles laid
    # end to end, and never shorter than the largest rectangle.
    sum_widths, sum_heights = sum(widths), sum(heights)
    max_width, max_height = max(widths), max(heights)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # pos_x[i], pos_y[i]: the lower-left corner of rectangle i, measured from the lower-left corner of the container
    pos_x = [model.add_var(name=f"pos_x_{i}", lb=0, ub=sum_widths - widths[i], var_type=mip.INTEGER)
             for i in range(n_rects)]
    pos_y = [model.add_var(name=f"pos_y_{i}", lb=0, ub=sum_heights - heights[i], var_type=mip.INTEGER)
             for i in range(n_rects)]

    # total_x and total_y: the width and the height of the container
    total_x = model.add_var(name="total_x", lb=max_width, ub=sum_widths, var_type=mip.INTEGER)
    total_y = model.add_var(name="total_y", lb=max_height, ub=sum_heights, var_type=mip.INTEGER)

    # width_is[a]: 1 when the container is a wide, for each candidate width a from max_width to sum_widths
    candidate_widths = range(max_width, sum_widths + 1)
    width_is = {a: model.add_var(name=f"width_is_{a}", var_type=mip.BINARY) for a in candidate_widths}
    # area_part[a]: one part of the container area, for the candidate width a
    area_part = {a: model.add_var(name=f"area_part_{a}", lb=0, ub=sum_heights) for a in candidate_widths}

    # The container is exactly one of the candidate widths.
    model += mip.xsum(width_is.values()) == 1
    model += total_x == mip.xsum(a * width_is[a] for a in candidate_widths)

    # area_part[a] is at most total_y, and equals total_y when the container is a wide.
    for a in candidate_widths:
        model += area_part[a] <= total_y
        model += area_part[a] <= sum_heights * width_is[a]
        model += area_part[a] >= total_y - sum_heights * (1 - width_is[a])

    # Minimise the container area, its width times its height.
    model.objective = mip.xsum(a * area_part[a] for a in candidate_widths)

    # Each rectangle lies inside the container.
    for i in range(n_rects):
        model += pos_x[i] + widths[i] <= total_x
        model += pos_y[i] + heights[i] <= total_y

    # No two rectangles overlap.
    for i in range(n_rects):
        for j in range(i + 1, n_rects):
            # i_left_of_j is 1 when rectangle i lies left of rectangle j
            i_left_of_j = model.add_var(name=f"i_left_of_j_{i}_{j}", var_type=mip.BINARY)
            # j_left_of_i is 1 when rectangle j lies left of rectangle i
            j_left_of_i = model.add_var(name=f"j_left_of_i_{i}_{j}", var_type=mip.BINARY)
            # i_below_j is 1 when rectangle i lies below rectangle j
            i_below_j = model.add_var(name=f"i_below_j_{i}_{j}", var_type=mip.BINARY)
            # j_below_i is 1 when rectangle j lies below rectangle i
            j_below_i = model.add_var(name=f"j_below_i_{i}_{j}", var_type=mip.BINARY)

            # One of the four separations holds. Each flag set to 1 forces its separation.
            model += mip.xsum([i_left_of_j, j_left_of_i, i_below_j, j_below_i]) >= 1
            model += pos_x[i] - pos_x[j] + sum_widths * i_left_of_j <= sum_widths - widths[i]
            model += pos_x[j] - pos_x[i] + sum_widths * j_left_of_i <= sum_widths - widths[j]
            model += pos_y[i] - pos_y[j] + sum_heights * i_below_j <= sum_heights - heights[i]
            model += pos_y[j] - pos_y[i] + sum_heights * j_below_i <= sum_heights - heights[j]

    outputs = {
        "pos_x": pos_x,
        "pos_y": pos_y,
        "total_x": total_x,
        "total_y": total_y,
    }
    return model, outputs


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
