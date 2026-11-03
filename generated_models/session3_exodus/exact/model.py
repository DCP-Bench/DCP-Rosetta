# session3_exodus: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install exact numpy`) with:
#   python session3_exodus.py

from exact import Exact


def create_model(instance):
    """Five children (Bernice, Carl, Debby, Sammy and Ted) each tell one part of the
    Exodus story, have a different age and come from a family from a different
    country. Find each child's age, country and story from the clues."""
    n = 5  # the five children, numbered 1 to 5
    # the five possible ages, each with the name used for it
    age_of = {"age3": 3, "age5": 5, "age7": 7, "age8": 8, "age10": 10}
    # the four categories; each lists the five possible values, one per child
    kinds = {
        "ages": list(age_of),
        "children": ["bernice", "carl", "debby", "sammy", "ted"],
        "countries": ["ethiopia", "kazakhstan", "lithuania", "morocco", "yemen"],
        "stories": ["burning_bush", "captivity", "moses_youth", "passover", "ten_commandments"],
    }

    solver = Exact()

    # Exact identifies its variables by name.
    # Each value is the number of its child, from 1 to 5. Values with the same number belong to the same child.
    # in_child[item][p-1] is 1 when the value belongs to child p, and 0 when not.
    in_child = {}
    for items in kinds.values():
        for item in items:
            solver.addVariable(item, 1, n)
            in_child[item] = [f"{item}_is_{p}" for p in range(1, n + 1)]
            for flag in in_child[item]:
                solver.addVariable(flag, 0, 1)

    # same_child[(x, y)] is the flag that is 1 exactly when values x and y belong to the same child.
    same_child = {}

    def same(x, y):
        """Return the flag that is 1 exactly when the values x and y belong to the same child."""
        if (x, y) not in same_child:
            name = f"same_{x}_{y}"
            solver.addVariable(name, 0, 1)
            for p in range(n):
                # Both values in child p set the flag to 1.
                solver.addConstraint([(1, name), (-1, in_child[x][p]), (-1, in_child[y][p])], True, -1)
                # x in child p while y is not sets the flag to 0.
                solver.addConstraint([(1, name), (1, in_child[x][p]), (-1, in_child[y][p])], False, 0, True, 1)
            same_child[(x, y)] = name
        return same_child[(x, y)]

    def clue(first, second, holds):
        """Rule out each pair of ages that breaks a clue: the child of age v1 is `first`,
        the child of age v2 is `second`, and holds(v1, v2) is false."""
        for a1, v1 in age_of.items():
            for a2, v2 in age_of.items():
                if not holds(v1, v2):
                    # This pair of ages is not allowed.
                    solver.addConstraint([(1, same(a1, first)), (1, same(a2, second))], False, 0, True, 1)

    for items in kinds.values():
        for item in items:
            # Each value belongs to exactly one child.
            solver.addConstraint([(1, flag) for flag in in_child[item]], True, 1, True, 1)
            # The number of a value is the number of the child it belongs to.
            solver.addConstraint([(p, in_child[item][p - 1]) for p in range(1, n + 1)] + [(-1, item)],
                                 True, 0, True, 0)
        # In each category every child number is used by exactly one value.
        for p in range(n):
            solver.addConstraint([(1, in_child[item][p]) for item in items], True, 1, True, 1)

    # Debby's family is from Lithuania.
    solver.addConstraint([(1, "debby"), (-1, "lithuania")], True, 0, True, 0)
    # The child who told the story of the Passover is two years older than Bernice.
    clue("passover", "bernice", lambda older, younger: older == younger + 2)
    # The child whose family is from Yemen is younger than the child from the Ethiopian family.
    clue("yemen", "ethiopia", lambda younger, older: younger < older)
    # The child from the Moroccan family is three years older than Ted.
    clue("morocco", "ted", lambda older, younger: older == younger + 3)
    # Sammy is three years older than the child who told the story of Moses's youth.
    clue("sammy", "moses_youth", lambda older, younger: older == younger + 3)

    return solver, kinds


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
