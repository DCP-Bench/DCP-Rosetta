# zebra: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python zebra.py

from pycsp3 import *


def create_model(instance):
    """The Zebra puzzle (sometimes referred to as Einstein's puzzle).
    There are five houses in a row, numbered from left to right.
    Each of the five houses is painted a different color, and has one inhabitant.
    The inhabitants are all of different nationalities, own different pets, drink different beverages and have different jobs."""
    n_houses = 5  # five houses in a row, numbered from left to right
    step = 1  # one house to the left or to the right

    # The index of each named value in its list, in the order the statement gives them.
    yellow, green, red, white, blue = range(n_houses)  # indices into colors
    italy, spain, japan, england, norway = range(n_houses)  # indices into nations
    cat, zebra, bear, snails, horse = range(n_houses)  # indices into pets
    milk, water, tea, coffee, juice = range(n_houses)  # indices into drinks
    painter, sculptor, diplomat, pianist, doctor = range(n_houses)  # indices into jobs

    # colors[c] is the house of the colour c.
    colors = VarArray(size=n_houses, dom=range(n_houses))
    # nations[n] is the house of the inhabitant of nationality n.
    nations = VarArray(size=n_houses, dom=range(n_houses))
    # pets[p] is the house of the pet p.
    pets = VarArray(size=n_houses, dom=range(n_houses))
    # drinks[d] is the house of the drink d.
    drinks = VarArray(size=n_houses, dom=range(n_houses))
    # jobs[j] is the house of the inhabitant with job j.
    jobs = VarArray(size=n_houses, dom=range(n_houses))

    satisfy(
        # Each colour, nationality, pet, drink and job is in a different house.
        [AllDifferent(attribute) for attribute in (colors, nations, pets, drinks, jobs)],

        # The painter owns the horse.
        pets[horse] == jobs[painter],

        # The diplomat drinks coffee.
        drinks[coffee] == jobs[diplomat],

        # The one who drinks milk lives in the white house.
        drinks[milk] == colors[white],

        # The Spaniard is a painter.
        nations[spain] == jobs[painter],

        # The Englishman lives in the red house.
        nations[england] == colors[red],

        # The snails are owned by the sculptor.
        pets[snails] == jobs[sculptor],

        # The green house is immediately on the left of the red one.
        colors[red] - colors[green] == step,

        # The Norwegian lives immediately on the right of the blue house.
        nations[norway] - colors[blue] == step,

        # The doctor drinks milk.
        drinks[milk] == jobs[doctor],

        # The diplomat is Japanese.
        nations[japan] == jobs[diplomat],

        # The Norwegian owns the zebra.
        pets[zebra] == nations[norway],

        # The green house is next to the white one.
        abs(colors[green] - colors[white]) == step,

        # The horse is owned by the neighbour of the diplomat.
        abs(pets[horse] - jobs[diplomat]) == step,

        # The Italian lives in the red, white or green house.
        Or(
            nations[italy] == colors[red],
            nations[italy] == colors[white],
            nations[italy] == colors[green],
        ),
    )

    return {
        "colors": colors,
        "nations": nations,
        "jobs": jobs,
        "pets": pets,
        "drinks": drinks,
    }


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
