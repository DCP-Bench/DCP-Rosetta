# zebra: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install cpmpy`) with:
#   python zebra.py

import cpmpy as cp


def create_model(instance):
    """The Zebra puzzle: five houses in a row, each with a different color,
    inhabitant nationality, pet, drink and job, fixed by a list of clues. Find the
    house number (0 to 4, left to right) of every color, nationality, job, pet and
    drink. The puzzle states all its clues itself, so instance is not used."""
    n_houses = 5

    # Each array holds, for each item, the number of the house it belongs to:
    # two items with the same number belong to the same house.
    colors = cp.intvar(0, n_houses - 1, shape=n_houses, name="colors")
    yellow, green, red, white, blue = colors
    nations = cp.intvar(0, n_houses - 1, shape=n_houses, name="nations")
    italy, spain, japan, england, norway = nations
    jobs = cp.intvar(0, n_houses - 1, shape=n_houses, name="jobs")
    painter, sculptor, diplomat, pianist, doctor = jobs
    pets = cp.intvar(0, n_houses - 1, shape=n_houses, name="pets")
    cat, zebra, bear, snails, horse = pets
    drinks = cp.intvar(0, n_houses - 1, shape=n_houses, name="drinks")
    milk, water, tea, coffee, juice = drinks

    model = cp.Model()

    # Each house has one color, one inhabitant, one pet, one drink and one job.
    model.add(cp.AllDifferent(colors))
    model.add(cp.AllDifferent(nations))
    model.add(cp.AllDifferent(jobs))
    model.add(cp.AllDifferent(pets))
    model.add(cp.AllDifferent(drinks))

    # The clues.
    model.add(painter == horse)
    model.add(diplomat == coffee)
    model.add(white == milk)
    model.add(spain == painter)
    model.add(england == red)
    model.add(snails == sculptor)
    model.add(green + 1 == red)       # the green house is immediately left of the red one
    model.add(blue + 1 == norway)     # the Norwegian lives immediately right of the blue house
    model.add(doctor == milk)
    model.add(japan == diplomat)
    model.add(norway == zebra)
    model.add(cp.abs(green - white) == 1)   # the green house is next to the white one
    model.add(cp.abs(horse - diplomat) == 1)  # the horse belongs to a neighbor of the diplomat
    model.add((italy == red) | (italy == white) | (italy == green))

    return model, {
        "colors": colors,
        "nations": nations,
        "jobs": jobs,
        "pets": pets,
        "drinks": drinks,
    }


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
