# zebra: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install cvc5 numpy`) with:
#   python zebra.py

import cvc5.pythonic as c5


def create_model(instance):
    """The Zebra puzzle: five houses in a row, numbered 0 (left) to 4 (right). Each
    house has a different color, nationality, pet, drink and job, and the clues
    below fix them. Find the house of every color, nationality, job, pet and drink."""
    # the house of each color
    yellow, green, red, white, blue = c5.Ints("yellow green red white blue")
    # the house of each nationality
    italy, spain, japan, england, norway = c5.Ints("italy spain japan england norway")
    # the house of each pet
    cat, zebra, bear, snails, horse = c5.Ints("cat zebra bear snails horse")
    # the house of each drink
    milk, water, tea, coffee, juice = c5.Ints("milk water tea coffee juice")
    # the house of each job
    painter, sculptor, diplomat, pianist, doctor = c5.Ints("painter sculptor diplomat pianist doctor")

    # the five colors
    colors = [yellow, green, red, white, blue]
    # the five nationalities
    nations = [italy, spain, japan, england, norway]
    # the five pets
    pets = [cat, zebra, bear, snails, horse]
    # the five drinks
    drinks = [milk, water, tea, coffee, juice]
    # the five jobs
    jobs = [painter, sculptor, diplomat, pianist, doctor]

    solver = c5.Solver()

    # The houses are numbered 0 to 4, and within each group the five items are in five different houses.
    for group in (colors, nations, pets, drinks, jobs):
        solver.add([v >= 0 for v in group])
        solver.add([v <= 4 for v in group])
        solver.add(c5.Distinct(group))

    # the painter owns the horse
    solver.add(painter == horse)
    # the diplomat drinks coffee
    solver.add(diplomat == coffee)
    # the one who drinks milk lives in the white house
    solver.add(milk == white)
    # the Spaniard is a painter
    solver.add(spain == painter)
    # the Englishman lives in the red house
    solver.add(england == red)
    # the snails are owned by the sculptor
    solver.add(snails == sculptor)
    # the green house is immediately on the left of the red one
    solver.add(green + 1 == red)
    # the Norwegian lives immediately on the right of the blue house
    solver.add(norway == blue + 1)
    # the doctor drinks milk
    solver.add(doctor == milk)
    # the diplomat is Japanese
    solver.add(japan == diplomat)
    # the Norwegian owns the zebra
    solver.add(norway == zebra)
    # the green house is next to the white one
    solver.add(c5.Or(green == white + 1, white == green + 1))
    # the horse is owned by the neighbor of the diplomat
    solver.add(c5.Or(horse == diplomat + 1, diplomat == horse + 1))
    # the Italian either lives in the red, white or green house
    solver.add(c5.Or(italy == red, italy == white, italy == green))

    outputs = {
        "colors": colors,
        "drinks": drinks,
        "jobs": jobs,
        "nations": nations,
        "pets": pets,
    }
    return solver, outputs


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
