# zebra: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install ortools`) with:
#   python zebra.py

from ortools.sat.python import cp_model


def create_model(instance):
    """The Zebra puzzle: five houses in a row, each with a different color,
    inhabitant nationality, pet, drink and job, fixed by a list of clues. Find the
    house number of every color, nationality, job, pet and drink."""
    # The houses, numbered 0 on the left to 4 on the right.
    n_houses = 5

    model = cp_model.CpModel()

    def house_block(prefix):
        # One variable per item: the number of the house it belongs to.
        return [model.new_int_var(0, n_houses - 1, f"{prefix}{i}")
                for i in range(n_houses)]

    def same_house(a, b, name):
        # Whether the two items a and b belong to the same house.
        same = model.new_bool_var(name)
        model.add(a == b).only_enforce_if(same)
        model.add(a != b).only_enforce_if(~same)
        return same

    # The five colors, nationalities, jobs, pets and drinks, in this order.
    colors = house_block("color")
    yellow, green, red, white, blue = colors
    nations = house_block("nation")
    italy, spain, japan, england, norway = nations
    jobs = house_block("job")
    painter, sculptor, diplomat, pianist, doctor = jobs
    pets = house_block("pet")
    cat, zebra, bear, snails, horse = pets
    drinks = house_block("drink")
    milk, water, tea, coffee, juice = drinks

    # Each house has one color, one nationality, one job, one pet and one drink.
    for group in (colors, nations, jobs, pets, drinks):
        model.add_all_different(group)

    # The painter owns the horse.
    model.add(painter == horse)
    # The diplomat drinks coffee.
    model.add(diplomat == coffee)
    # The one who drinks milk lives in the white house.
    model.add(white == milk)
    # The Spaniard is a painter.
    model.add(spain == painter)
    # The Englishman lives in the red house.
    model.add(england == red)
    # The snails are owned by the sculptor.
    model.add(snails == sculptor)
    # The green house is immediately on the left of the red one.
    model.add(green + 1 == red)
    # The Norwegian lives immediately on the right of the blue house.
    model.add(blue + 1 == norway)
    # The doctor drinks milk.
    model.add(doctor == milk)
    # The diplomat is Japanese.
    model.add(japan == diplomat)
    # The Norwegian owns the zebra.
    model.add(norway == zebra)

    # The green house is next to the white one, on either side.
    green_white_gap = model.new_int_var(0, n_houses - 1, "green_white_gap")
    model.add_abs_equality(green_white_gap, green - white)
    model.add(green_white_gap == 1)

    # The horse is owned by a neighbor of the diplomat.
    horse_diplomat_gap = model.new_int_var(0, n_houses - 1, "horse_diplomat_gap")
    model.add_abs_equality(horse_diplomat_gap, horse - diplomat)
    model.add(horse_diplomat_gap == 1)

    # The Italian either lives in the red, white or green house.
    model.add_bool_or([
        same_house(italy, red, "italy_red"),
        same_house(italy, white, "italy_white"),
        same_house(italy, green, "italy_green"),
    ])

    return model, {
        "colors": colors,
        "nations": nations,
        "jobs": jobs,
        "pets": pets,
        "drinks": drinks,
    }


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
