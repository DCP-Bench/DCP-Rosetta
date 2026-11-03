# session3_exodus: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python session3_exodus.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Five children at Hebrew school (Bernice, Carl, Debby, Sammy and Ted) each tell
    one part of the Exodus story. Each child is a different age (3, 5, 7, 8 or 10),
    and each family came to America from a different country. Find each child's age,
    country and story from the clues."""
    n = 5  # the number of children
    age_values = [3, 5, 7, 8, 10]  # the possible ages, in years

    pool = IDPool()  # hands out the variable numbers

    def slots(name):
        """Five slots, one per member of a category. Each holds the number, from 1 to 5,
        of the child that member belongs to."""
        return [Integer(f"{name}{i}", 1, n, vpool=pool) for i in range(n)]

    # ages[k] is the child aged age_values[k]
    ages = slots("age")
    # children[k] is the child called Bernice, Carl, Debby, Sammy and Ted, in that order
    children = slots("child")
    # countries[k] is the child whose family came from the k-th country: Ethiopia,
    # Kazakhstan, Lithuania, Morocco and Yemen, in that order
    countries = slots("country")
    # stories[k] is the child who tells the k-th story: burning bush, captivity, Moses's
    # youth, Passover and the Ten Commandments, in that order
    stories = slots("story")

    # Names for the children, countries and stories used in the clues.
    bernice, carl, debby, sammy, ted = children
    ethiopia, kazakhstan, lithuania, morocco, yemen = countries
    burning_bush, captivity, moses_youth, passover, ten_commandments = stories

    # Constraints on the slots, added below.
    engine = IntegerEngine(vars=ages + children + countries + stories, vpool=pool)

    same_child = {}  # the flag already made for each pair of slots

    def same(x, y):
        """A flag that is true exactly when slots x and y hold the same child."""
        if (x, y) not in same_child:
            flag = pool.id(("same", x.name, y.name))
            # Equal numbers make the flag true, and a true flag forces equal numbers.
            for number in range(1, n + 1):
                cnf.append([-x.equals(number), -y.equals(number), flag])
                for other in range(1, n + 1):
                    if other != number:
                        cnf.append([-flag, -x.equals(number), -y.equals(other)])
            same_child[(x, y)] = flag
        return same_child[(x, y)]

    def clue(child_a, child_b, holds):
        """Rule out each pair of ages that breaks a clue: when child_a has age a and
        child_b has age b, holds(a, b) must be true."""
        for i, age_i in enumerate(ages):
            for j, age_j in enumerate(ages):
                if not holds(age_values[i], age_values[j]):
                    cnf.append([-same(age_i, child_a), -same(age_j, child_b)])

    # Within each category, no two slots hold the same child.
    for category in (ages, children, countries, stories):
        engine.add_alldifferent(category)

    # Debby's family is from Lithuania.
    engine.add_equal(debby, lithuania)

    cnf = engine.clausify()

    # The child who told the story of Passover is two years older than Bernice.
    clue(passover, bernice, lambda a, b: a == b + 2)
    # The child whose family is from Yemen is younger than the child from the Ethiopian family.
    clue(yemen, ethiopia, lambda a, b: a < b)
    # The child from the Moroccan family is three years older than Ted.
    clue(morocco, ted, lambda a, b: a == b + 3)
    # Sammy is three years older than the child who told the story of Moses's youth.
    clue(sammy, moses_youth, lambda a, b: a == b + 3)

    return cnf, {"ages": ages, "children": children, "countries": countries, "stories": stories}


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
