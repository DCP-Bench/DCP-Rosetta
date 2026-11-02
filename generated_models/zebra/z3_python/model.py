# zebra: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install z3-solver numpy`) with:
#   python zebra.py

import z3


def create_model(instance):
    """Five houses in a row, numbered 0 on the left to 4 on the right. Each house has a
    color, an inhabitant of one nationality, a pet, a drink and a job, and no two houses
    share one of these. Find the house of every color, nationality, job, pet and drink so
    that all the clues hold."""
    n_houses = 5

    # Each variable is the number of the house that has this color, nationality, job, pet or drink.
    # Two variables with the same number belong to the same house.
    colors = z3.Ints("yellow green red white blue")
    yellow, green, red, white, blue = colors
    nations = z3.Ints("italy spain japan england norway")
    italy, spain, japan, england, norway = nations
    jobs = z3.Ints("painter sculptor diplomat pianist doctor")
    painter, sculptor, diplomat, pianist, doctor = jobs
    pets = z3.Ints("cat zebra bear snails horse")
    cat, zebra, bear, snails, horse = pets
    drinks = z3.Ints("milk water tea coffee juice")
    milk, water, tea, coffee, juice = drinks

    solver = z3.Solver()

    # Every item is in a house, and no two items of one kind share a house.
    for group in (colors, nations, jobs, pets, drinks):
        solver.add([z3.And(v >= 0, v <= n_houses - 1) for v in group])
        solver.add(z3.Distinct(group))

    # The painter owns the horse.
    solver.add(painter == horse)
    # The diplomat drinks coffee.
    solver.add(diplomat == coffee)
    # The one who drinks milk lives in the white house.
    solver.add(white == milk)
    # The Spaniard is a painter.
    solver.add(spain == painter)
    # The Englishman lives in the red house.
    solver.add(england == red)
    # The snails are owned by the sculptor.
    solver.add(snails == sculptor)
    # The green house is immediately left of the red one.
    solver.add(green + 1 == red)
    # The Norwegian lives immediately right of the blue house.
    solver.add(blue + 1 == norway)
    # The doctor drinks milk.
    solver.add(doctor == milk)
    # The diplomat is Japanese.
    solver.add(japan == diplomat)
    # The Norwegian owns the zebra.
    solver.add(norway == zebra)
    # The green house is next to the white one, on either side.
    solver.add(z3.Abs(green - white) == 1)
    # The horse is owned by a neighbor of the diplomat.
    solver.add(z3.Or(horse == diplomat - 1, horse == diplomat + 1))
    # The Italian lives in the red, white or green house.
    solver.add(z3.Or(italy == red, italy == white, italy == green))

    return solver, {"colors": colors, "nations": nations, "jobs": jobs, "pets": pets, "drinks": drinks}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
