# zebra: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install mip numpy`) with:
#   python zebra.py

import mip


def create_model(instance):
    """The Zebra puzzle: five houses in a row, each with a different color,
    inhabitant nationality, pet, drink and job, fixed by a list of clues. Find the
    house number of every color, nationality, job, pet and drink."""
    n_houses = 5  # five houses in a row, numbered 0 (left) to 4 (right); each category has one value per house

    # The values of each category.
    CATEGORIES = {
        "colors": ["yellow", "green", "red", "white", "blue"],
        "nations": ["italy", "spain", "japan", "england", "norway"],
        "pets": ["cat", "zebra", "bear", "snails", "horse"],
        "drinks": ["milk", "water", "tea", "coffee", "juice"],
        "jobs": ["painter", "sculptor", "diplomat", "pianist", "doctor"],
    }

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[c][i][h] is true when the value CATEGORIES[c][i] is in house h.
    x = {}
    # pos[c][i] is the house number of the value CATEGORIES[c][i].
    pos = {}
    for c, values in CATEGORIES.items():
        x[c] = {}
        pos[c] = {}
        for i, name in enumerate(values):
            x[c][i] = [
                model.add_var(f"x_{c}_{name}_{h}", var_type=mip.BINARY)
                for h in range(n_houses)
            ]
            # Each value is in exactly one house.
            model.add_constr(mip.xsum(x[c][i]) == 1, name=f"one_house_{c}_{name}")
            pos[c][i] = model.add_var(f"pos_{c}_{name}", lb=0, ub=n_houses - 1, var_type=mip.INTEGER)
            # The house number of a value is the house it is in.
            model.add_constr(
                pos[c][i] == mip.xsum(h * x[c][i][h] for h in range(n_houses)),
                name=f"pos_{c}_{name}_def",
            )
        # Each house holds exactly one value of each category.
        for h in range(n_houses):
            model.add_constr(
                mip.xsum(x[c][i][h] for i in range(n_houses)) == 1,
                name=f"one_value_{c}_house_{h}",
            )

    # The house number of the value name in category c.
    def p(c, name):
        return pos[c][CATEGORIES[c].index(name)]

    # The two values are in the same house.
    def same_house(a, b, label):
        model.add_constr(a - b == 0, name=label)

    # a is in the house immediately to the left of b.
    def left_of(a, b, label):
        model.add_constr(a == b - 1, name=label)

    # a and b are in neighboring houses. Their difference is 1 or -1, and s[label] is true
    # when a is to the right of b.
    def next_to(a, b, label):
        s = model.add_var(f"s_{label}", var_type=mip.BINARY)
        model.add_constr(a - b == 2 * s - 1, name=label)

    # The painter owns the horse.
    same_house(p("jobs", "painter"), p("pets", "horse"), "painter_owns_horse")
    # The diplomat drinks coffee.
    same_house(p("jobs", "diplomat"), p("drinks", "coffee"), "diplomat_drinks_coffee")
    # The one who drinks milk lives in the white house.
    same_house(p("drinks", "milk"), p("colors", "white"), "milk_in_white_house")
    # The Spaniard is a painter.
    same_house(p("nations", "spain"), p("jobs", "painter"), "spaniard_is_painter")
    # The Englishman lives in the red house.
    same_house(p("nations", "england"), p("colors", "red"), "englishman_in_red_house")
    # The snails are owned by the sculptor.
    same_house(p("pets", "snails"), p("jobs", "sculptor"), "snails_owned_by_sculptor")
    # The green house is immediately on the left of the red one.
    left_of(p("colors", "green"), p("colors", "red"), "green_left_of_red")
    # The Norwegian lives immediately on the right of the blue house.
    left_of(p("colors", "blue"), p("nations", "norway"), "norwegian_right_of_blue")
    # The doctor drinks milk.
    same_house(p("jobs", "doctor"), p("drinks", "milk"), "doctor_drinks_milk")
    # The diplomat is Japanese.
    same_house(p("jobs", "diplomat"), p("nations", "japan"), "diplomat_is_japanese")
    # The Norwegian owns the zebra.
    same_house(p("nations", "norway"), p("pets", "zebra"), "norwegian_owns_zebra")
    # The green house is next to the white one.
    next_to(p("colors", "green"), p("colors", "white"), "green_next_to_white")
    # The horse is owned by the neighbor of the diplomat.
    next_to(p("pets", "horse"), p("jobs", "diplomat"), "horse_owner_neighbor_of_diplomat")

    # t[k] is true when the Italian lives in the house of the color k. He lives in exactly
    # one of the red, white and green houses.
    t = {
        k: model.add_var(f"t_italian_{k}", var_type=mip.BINARY)
        for k in ["red", "white", "green"]
    }
    model.add_constr(mip.xsum(t.values()) == 1, name="italian_one_of_three_houses")
    # When t[k] is true, the Italian and the color k are in the same house. When it is
    # false, the two house numbers differ by at most n_houses - 1, which always holds.
    for k in ["red", "white", "green"]:
        model.add_constr(
            p("nations", "italy") - p("colors", k) <= (n_houses - 1) * (1 - t[k]),
            name=f"italian_in_{k}_upper",
        )
        model.add_constr(
            p("colors", k) - p("nations", "italy") <= (n_houses - 1) * (1 - t[k]),
            name=f"italian_in_{k}_lower",
        )

    # The house number of each color, nation, pet, drink and job.
    outputs = {
        "colors": [pos["colors"][i] for i in range(n_houses)],
        "drinks": [pos["drinks"][i] for i in range(n_houses)],
        "jobs": [pos["jobs"][i] for i in range(n_houses)],
        "nations": [pos["nations"][i] for i in range(n_houses)],
        "pets": [pos["pets"][i] for i in range(n_houses)],
    }
    return model, outputs


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
