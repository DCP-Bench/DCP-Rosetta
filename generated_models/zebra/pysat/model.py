# zebra: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python zebra.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Five houses stand in a row, numbered 0 to 4 from left to right. Each house has its own
    color, inhabitant nationality, job, pet and drink. The clues say who lives next to whom.
    Find the house of every color, nationality, job, pet and drink."""
    n_houses = 5  # the houses, numbered 0 to 4 from left to right

    pool = IDPool()  # gives each house number below its own variable

    def houses(name):
        # the house of each of the five members of a category, as a number from 0 to 4
        return [Integer(f"{name}{i}", 0, n_houses - 1, vpool=pool) for i in range(n_houses)]

    def forbidden_pairs(x, y, holds):
        # every pair of houses for x and y where holds is false
        return [[-x.equals(p), -y.equals(q)]
                for p in range(n_houses) for q in range(n_houses) if not holds(p, q)]

    # the house of each color, in the order yellow, green, red, white, blue
    colors = houses("color")
    yellow, green, red, white, blue = colors
    # the house of each nationality, in the order italy, spain, japan, england, norway
    nations = houses("nation")
    italy, spain, japan, england, norway = nations
    # the house of each job, in the order painter, sculptor, diplomat, pianist, doctor
    jobs = houses("job")
    painter, sculptor, diplomat, pianist, doctor = jobs
    # the house of each pet, in the order cat, zebra, bear, snails, horse
    pets = houses("pet")
    cat, zebra, bear, snails, horse = pets
    # the house of each drink, in the order milk, water, tea, coffee, juice
    drinks = houses("drink")
    milk, water, tea, coffee, juice = drinks

    engine = IntegerEngine(vars=colors + nations + jobs + pets + drinks, vpool=pool)

    # Each house has one color, one nationality, one job, one pet and one drink, so the
    # members of each category are in different houses.
    for category in (colors, nations, jobs, pets, drinks):
        engine.add_alldifferent(category)

    # The clues that put two things in the same house.
    same_house = [
        (painter, horse),    # the painter owns the horse
        (diplomat, coffee),  # the diplomat drinks coffee
        (white, milk),       # the one who drinks milk lives in the white house
        (spain, painter),    # the Spaniard is a painter
        (england, red),      # the Englishman lives in the red house
        (snails, sculptor),  # the snails are owned by the sculptor
        (doctor, milk),      # the doctor drinks milk
        (japan, diplomat),   # the diplomat is Japanese
        (norway, zebra),     # the Norwegian owns the zebra
    ]
    for x, y in same_house:
        engine.add_equal(x, y)

    cnf = engine.clausify()  # the constraints of the puzzle

    # The green house is immediately on the left of the red one.
    cnf.extend(forbidden_pairs(green, red, lambda g, r: g + 1 == r))
    # The Norwegian lives immediately on the right of the blue house.
    cnf.extend(forbidden_pairs(blue, norway, lambda b, o: b + 1 == o))
    # The green house is next to the white one.
    cnf.extend(forbidden_pairs(green, white, lambda g, w: abs(g - w) == 1))
    # The horse is owned by the neighbour of the diplomat.
    cnf.extend(forbidden_pairs(diplomat, horse, lambda d, h: abs(d - h) == 1))
    # The Italian lives in the red, white or green house.
    for house in range(n_houses):
        cnf.append([-italy.equals(house), red.equals(house), white.equals(house),
                    green.equals(house)])

    return cnf, {"colors": colors, "nations": nations, "jobs": jobs, "pets": pets, "drinks": drinks}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
