# session3_exodus: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install cpmpy`) with:
#   python session3_exodus.py

import cpmpy as cp


def create_model(instance):
    """Five children (Bernice, Carl, Debby, Sammy and Ted) each present a part of
    the Exodus story, have a different age and come from a family from a
    different country. Find each child's age, country and story from the clues.
    The puzzle states its own entities, so the instance is not used."""
    # Every variable holds a group number 1..5: variables from different
    # categories with the same number describe the same child.

    # ages[k] is the group of the k-th age, in order 3, 5, 7, 8, 10
    ages = cp.intvar(1, 5, shape=5, name="ages")
    # children[k] is the group of the k-th child, in order Bernice, Carl, Debby, Sammy, Ted
    children = cp.intvar(1, 5, shape=5, name="children")
    # countries[k] is the group of the k-th country, in order Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen
    countries = cp.intvar(1, 5, shape=5, name="countries")
    # stories[k] is the group of the k-th story, in order burning bush, captivity, Moses's youth, Passover, Ten Commandments
    stories = cp.intvar(1, 5, shape=5, name="stories")

    bernice, carl, debby, sammy, ted = children
    ethiopia, kazakhstan, lithuania, morocco, yemen = countries
    burning_bush, captivity, moses_youth, passover, ten_commandments = stories

    # the actual age that each slot of ages stands for
    age_values = [3, 5, 7, 8, 10]

    def age(group):
        """The actual age of the child in `group`."""
        return cp.sum([value * (ages[k] == group) for k, value in enumerate(age_values)])

    model = cp.Model()
    # Each category gives every child a different value.
    model.add(cp.AllDifferent(ages))
    model.add(cp.AllDifferent(children))
    model.add(cp.AllDifferent(countries))
    model.add(cp.AllDifferent(stories))
    # 1. Debby's family is from Lithuania.
    model.add(debby == lithuania)
    # 2. The Passover child is two years older than Bernice.
    model.add(age(passover) == age(bernice) + 2)
    # 3. The Yemeni child is younger than the Ethiopian child.
    model.add(age(yemen) < age(ethiopia))
    # 4. The Moroccan child is three years older than Ted.
    model.add(age(morocco) == age(ted) + 3)
    # 5. Sammy is three years older than the child who told of Moses's youth.
    model.add(age(sammy) == age(moses_youth) + 3)

    return model, {
        "ages": ages,
        "children": children,
        "countries": countries,
        "stories": stories,
    }


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
