# session3_exodus: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install z3-solver numpy`) with:
#   python session3_exodus.py

import z3


def create_model(instance):
    """Five children at Hebrew school each tell one part of the Exodus story. Each
    child is a different age (3, 5, 7, 8 or 10), and each family came to America
    from a different country. Find each child's age, country and story from the clues."""
    # The possible ages in years, in the order of the ages list.
    age_values = [3, 5, 7, 8, 10]

    # Each child has a number from 1 to 5; the same number in two lists is the same child.
    # ages[k]: the number of the child who is age_values[k] years old.
    ages = z3.IntVector("ages", 5)
    # children[k]: the number of the child called Bernice, Carl, Debby, Sammy and Ted, in that order.
    children = z3.IntVector("children", 5)
    # countries[k]: the number of the child whose family is from Ethiopia, Kazakhstan, Lithuania, Morocco and Yemen, in that order.
    countries = z3.IntVector("countries", 5)
    # stories[k]: the number of the child who tells the burning bush, captivity, Moses's youth, Passover and Ten Commandments story, in that order.
    stories = z3.IntVector("stories", 5)

    # The child number of each named child, country and story.
    bernice, carl, debby, sammy, ted = children
    ethiopia, kazakhstan, lithuania, morocco, yemen = countries
    burning_bush, captivity, moses_youth, passover, ten_commandments = stories

    def age_of(child):
        # The age in years of the child with this number.
        age = z3.IntVal(age_values[-1])
        for k in reversed(range(len(age_values) - 1)):
            age = z3.If(ages[k] == child, age_values[k], age)
        return age

    solver = z3.Solver()

    # Child numbers run from 1 to 5.
    solver.add([z3.And(1 <= v, v <= 5) for v in ages + children + countries + stories])

    # Each age, name, country and story belongs to exactly one child.
    solver.add([z3.Distinct(group) for group in (ages, children, countries, stories)])

    # Debby's family is from Lithuania.
    solver.add(debby == lithuania)

    # The child who told the Passover story is two years older than Bernice.
    solver.add(age_of(passover) == age_of(bernice) + 2)

    # The child whose family is from Yemen is younger than the child whose family is from Ethiopia.
    solver.add(age_of(yemen) < age_of(ethiopia))

    # The child whose family is from Morocco is three years older than Ted.
    solver.add(age_of(morocco) == age_of(ted) + 3)

    # Sammy is three years older than the child who told the story of Moses's youth.
    solver.add(age_of(sammy) == age_of(moses_youth) + 3)

    outputs = {"ages": ages, "children": children, "countries": countries, "stories": stories}
    return solver, outputs


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
