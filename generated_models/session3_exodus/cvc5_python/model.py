# session3_exodus: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install cvc5 numpy`) with:
#   python session3_exodus.py

import cvc5.pythonic as c5


def create_model(instance):
    """Five children at Hebrew school each tell one part of the Exodus story. Each child
    has a different age, and each family came to America from a different country.
    Find each child's age, family country and story."""
    # The ages in years.
    age_values = [3, 5, 7, 8, 10]

    # Each child is a number from 1 to 5, and the same number in every list is the same child.
    # ages[k] is the child who is age_values[k] years old.
    ages = [c5.Int(f"ages_{k}") for k in range(5)]
    # children[k] is the child called Bernice, Carl, Debby, Sammy and Ted, in that order.
    children = [c5.Int(f"children_{k}") for k in range(5)]
    # countries[k] is the child whose family is from Ethiopia, Kazakhstan, Lithuania, Morocco and Yemen, in that order.
    countries = [c5.Int(f"countries_{k}") for k in range(5)]
    # stories[k] is the child who tells the burning bush, captivity, Moses's youth, Passover and Ten Commandments parts, in that order.
    stories = [c5.Int(f"stories_{k}") for k in range(5)]

    # The child numbers of the children, countries and stories named in the clues.
    bernice, _, debby, sammy, ted = children
    ethiopia, _, lithuania, morocco, yemen = countries
    _, _, moses_youth, passover, _ = stories

    def age_of(child):
        """The age of the child with this number."""
        return c5.Sum([c5.If(slot == child, years, 0) for slot, years in zip(ages, age_values)])

    solver = c5.Solver()

    # Each list uses the numbers 1 to 5, each once, so every child has one age, one family country and one story.
    for values in (ages, children, countries, stories):
        solver.add([value >= 1 for value in values])
        solver.add([value <= 5 for value in values])
        solver.add(c5.Distinct(values))

    # Debby's family is from Lithuania.
    solver.add(lithuania == debby)
    # The child who told the story of Passover is two years older than Bernice.
    solver.add(age_of(passover) == age_of(bernice) + 2)
    # The child whose family is from Yemen is younger than the child from the Ethiopian family.
    solver.add(age_of(yemen) < age_of(ethiopia))
    # The child from the Moroccan family is three years older than Ted.
    solver.add(age_of(morocco) == age_of(ted) + 3)
    # Sammy is three years older than the child who told the story of Moses's youth.
    solver.add(age_of(sammy) == age_of(moses_youth) + 3)

    return solver, {
        "ages": ages,
        "children": children,
        "countries": countries,
        "stories": stories,
    }


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
