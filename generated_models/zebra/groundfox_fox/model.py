# zebra: a FOX model for GroundFOX from DCP Rosetta.
#
# The Zebra puzzle (sometimes referred to as Einstein's puzzle) is defined as follows. There
# are five houses in a row, numbered from left to right. Each of the five houses is painted a
# different color, and has one inhabitant. The inhabitants are all of different nationalities,
# own different pets, drink different beverages and have different jobs. We know that: -
# colors are yellow, green, red, white, and blue - nations of inhabitants are italy, spain,
# japan, england, and norway - pets are cat, zebra, bear, snails, and horse - drinks are milk,
# water, tea, coffee, and juice - jobs are painter, sculptor, diplomat, pianist, and doctor -
# the painter owns the horse - the diplomat drinks coffee - the one who drinks milk lives in
# the white house - the Spaniard is a painter - the Englishman lives in the red house - the
# snails are owned by the sculptor - the green house is immediately on the left of the red one
# - the Norwegian lives immediately on the right of the blue house - the doctor drinks milk -
# the diplomat is Japanese - the Norwegian owns the zebra - the green house is next to the
# white one - the horse is owned by the neighbor of the diplomat - the Italian either lives in
# the red, white or green house
#
# Print the numbers - between 0 and 4 - representing the house of each inhabitant (colors,
# nations, jobs, pets, drinks). The same number represents the same house.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py zebra.json --check

"""zebra: a FOX model for GroundFOX from DCP Rosetta.

Each attribute table X(v, h) says attribute value v (index in the order of the
description) lives in house h. Each table is a bijection between its values and the
five houses. Clues are same-house, adjacency and next-house relations on the houses.
"""

ATTRS = ["colors", "nations", "jobs", "pets", "drinks"]


def _bijection(x):
    return (
        f"! v [Val(v)] : ? h [House(h)] : {x}(v, h).\n"
        f"! v [Val(v)] : ! h [House(h)] : ! g [House(g) & h ~= g] : ~{x}(v, h) | ~{x}(v, g).\n"
        f"! h [House(h)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~{x}(v, h) | ~{x}(w, h).\n"
    )


def _same(x, v, y, w):
    # Value v of table x and value w of table y share a house.
    return (
        f"! h [House(h)] : ~{x}({v}, h) | {y}({w}, h).\n"
        f"! h [House(h)] : ~{y}({w}, h) | {x}({v}, h).\n"
    )


# Index conventions (order of the description):
# colors: yellow 0, green 1, red 2, white 3, blue 4
# nations: italy 0, spain 1, japan 2, england 3, norway 4
# pets: cat 0, zebra 1, bear 2, snails 3, horse 4
# drinks: milk 0, water 1, tea 2, coffee 3, juice 4
# jobs: painter 0, sculptor 1, diplomat 2, pianist 3, doctor 4
CLUES = (
    _same("jobs", 0, "pets", 4)        # painter owns the horse
    + _same("jobs", 2, "drinks", 3)    # diplomat drinks coffee
    + _same("drinks", 0, "colors", 3)  # milk drinker lives in the white house
    + _same("nations", 1, "jobs", 0)   # Spaniard is a painter
    + _same("nations", 3, "colors", 2) # Englishman lives in the red house
    + _same("pets", 3, "jobs", 1)      # snails owned by the sculptor
    + _same("jobs", 4, "drinks", 0)    # doctor drinks milk
    + _same("jobs", 2, "nations", 2)   # diplomat is Japanese
    + _same("nations", 4, "pets", 1)   # Norwegian owns the zebra
    # green immediately left of red
    + "! h [House(h) & ? z : Next(h, z)] : ? g [Next(h, g)] : colors(2, g) | ~colors(1, h).\n"
    + "! h [House(h) & ~? z : Next(h, z)] : ~colors(1, h).\n"
    # Norwegian immediately right of blue
    + "! h [House(h) & ? z : Next(h, z)] : ? g [Next(h, g)] : nations(4, g) | ~colors(4, h).\n"
    + "! h [House(h) & ~? z : Next(h, z)] : ~colors(4, h).\n"
    # green next to white
    + "! h [House(h)] : ? g [Adj(h, g)] : colors(3, g) | ~colors(1, h).\n"
    # horse owned by a neighbour of the diplomat
    + "! h [House(h)] : ? g [Adj(h, g)] : pets(4, g) | ~jobs(2, h).\n"
    # Italian lives in the red, white or green house
    + "! h [House(h)] : ~nations(0, h) | colors(1, h) | colors(2, h) | colors(3, h).\n"
)

FOX = (
    "invocabulary { House/1 Val/1 Next/2 Adj/2 }\n"
    "outvocabulary { " + " ".join(f"{a}/2" for a in ATTRS) + " }\n"
    "theory {\n"
    + "".join(_bijection(a) for a in ATTRS)
    + CLUES
    + "}\n"
)


def structure(instance):
    return {
        "House": range(5),
        "Val": range(5),
        "Next": [(h, h + 1) for h in range(4)],
        "Adj": [(h, g) for h in range(5) for g in range(5) if abs(h - g) == 1],
    }
