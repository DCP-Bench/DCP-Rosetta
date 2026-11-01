# zebra: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install pychoco numpy`) with:
#   python zebra.py

from pychoco.model import Model


def create_model(instance):
    """The Zebra puzzle: five houses in a row, each with a different color,
    inhabitant nationality, pet, drink and job, fixed by a list of clues. Find the
    house number (0 to 4, left to right) of every color, nationality, job, pet and
    drink."""
    n_houses = 5  # the five houses, numbered 0 on the left to 4 on the right

    model = Model()

    def house_block(prefix):
        # One variable per item: the number of the house it belongs to.
        return [model.intvar(0, n_houses - 1, name=f"{prefix}{i}") for i in range(n_houses)]

    # The house of each color, in the order yellow, green, red, white, blue.
    colors = house_block("color")
    yellow, green, red, white, blue = colors
    # The house of each nationality, in the order Italian, Spanish, Japanese, English, Norwegian.
    nations = house_block("nation")
    italy, spain, japan, england, norway = nations
    # The house of each job, in the order painter, sculptor, diplomat, pianist, doctor.
    jobs = house_block("job")
    painter, sculptor, diplomat, pianist, doctor = jobs
    # The house of each pet, in the order cat, zebra, bear, snails, horse.
    pets = house_block("pet")
    cat, zebra, bear, snails, horse = pets
    # The house of each drink, in the order milk, water, tea, coffee, juice.
    drinks = house_block("drink")
    milk, water, tea, coffee, juice = drinks

    # Each house has one color, one nationality, one job, one pet and one drink.
    for group in (colors, nations, jobs, pets, drinks):
        model.all_different(group).post()

    # The painter owns the horse.
    model.arithm(painter, "=", horse).post()
    # The diplomat drinks coffee.
    model.arithm(diplomat, "=", coffee).post()
    # The one who drinks milk lives in the white house.
    model.arithm(white, "=", milk).post()
    # The Spaniard is a painter.
    model.arithm(spain, "=", painter).post()
    # The Englishman lives in the red house.
    model.arithm(england, "=", red).post()
    # The snails are owned by the sculptor.
    model.arithm(snails, "=", sculptor).post()
    # The doctor drinks milk.
    model.arithm(doctor, "=", milk).post()
    # The diplomat is Japanese.
    model.arithm(japan, "=", diplomat).post()
    # The Norwegian owns the zebra.
    model.arithm(norway, "=", zebra).post()
    # The green house is immediately on the left of the red one.
    model.arithm(green, "+", 1, "=", red).post()
    # The Norwegian lives immediately on the right of the blue house.
    model.arithm(blue, "+", 1, "=", norway).post()
    # The green house is next to the white one, on either side.
    model.distance(green, white, "=", 1).post()
    # The horse is owned by a neighbor of the diplomat.
    model.distance(horse, diplomat, "=", 1).post()
    # The Italian lives in the red, white or green house.
    model.or_([
        model.arithm(italy, "=", red),
        model.arithm(italy, "=", white),
        model.arithm(italy, "=", green),
    ]).post()

    return model, {
        "colors": colors, "nations": nations, "jobs": jobs,
        "pets": pets, "drinks": drinks,
    }, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
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
