# session3_exodus: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install mip numpy`) with:
#   python session3_exodus.py

import mip


def create_model(instance):
    """Five children at Hebrew school (Bernice, Carl, Debby, Sammy and Ted) each
    tell one part of the Exodus story. Each child is a different age (3, 5, 7, 8
    or 10), and each family came to America from a different country. Find each
    child's age, country and story from the clues."""
    n = 5  # the number of children, ages, countries and stories
    possible_ages = [3, 5, 7, 8, 10]  # the ages of the children, in years

    # Positions of the children, countries and stories in the puzzle's lists.
    bernice, carl, debby, sammy, ted = range(n)
    ethiopia, kazakhstan, lithuania, morocco, yemen = range(n)
    burning_bush, captivity, moses_youth, passover, ten_commandments = range(n)

    model = mip.Model(solver_name="CBC")

    # in_group[cat][e][g] is 1 when entity e of category cat is in group g. A group
    # holds one child, one age, one country and one story.
    categories = ["age", "child", "country", "story"]
    in_group = {
        cat: [[model.add_var(f"{cat}_{e}_in_group_{g}", var_type=mip.BINARY) for g in range(n)] for e in range(n)]
        for cat in categories
    }

    # same_group is 1 when entity e1 of cat1 and entity e2 of cat2 are in the same group.
    def same_group(cat1, e1, cat2, e2):
        same = model.add_var(f"same_{cat1}_{e1}_{cat2}_{e2}", var_type=mip.BINARY)
        for g in range(n):
            a = in_group[cat1][e1][g]
            b = in_group[cat2][e2][g]
            model.add_constr(same >= a + b - 1)
            model.add_constr(same <= 1 - a + b)
            model.add_constr(same <= 1 + a - b)
        return same

    # The age of child c: the possible age that the child is given.
    def age(c):
        return mip.xsum(possible_ages[a] * child_age[c][a] for a in range(n))

    # Ages differ by at most 7 years and a clue shifts the difference by 3, so 20 is
    # large enough to switch off a clue that does not apply to a child.
    big_m = 20

    # If flag is 1, the difference expr equals rhs.
    def implies_difference(flag, expr, rhs):
        model.add_constr(expr - rhs <= big_m * (1 - flag))
        model.add_constr(expr - rhs >= -big_m * (1 - flag))

    # The group number (1 to 5) of entity e of category cat.
    def group_number(cat, e):
        return mip.xsum((g + 1) * in_group[cat][e][g] for g in range(n))

    # Each entity is in exactly one group.
    for cat in categories:
        for e in range(n):
            model.add_constr(mip.xsum(in_group[cat][e]) == 1)

    # Each group holds exactly one entity of each category.
    for cat in categories:
        for g in range(n):
            model.add_constr(mip.xsum(in_group[cat][e][g] for e in range(n)) == 1)

    # child_age[c][a] is 1 when child c has age possible_ages[a].
    child_age = [[same_group("child", c, "age", a) for a in range(n)] for c in range(n)]
    # child_country[c][k] is 1 when child c comes from country k.
    child_country = [[same_group("child", c, "country", k) for k in range(n)] for c in range(n)]
    # child_story[c][s] is 1 when child c tells story s.
    child_story = [[same_group("child", c, "story", s) for s in range(n)] for c in range(n)]

    # Debby's family is from Lithuania.
    model.add_constr(child_country[debby][lithuania] == 1)

    # The child who told the Passover story is two years older than Bernice, so
    # Bernice did not tell it.
    for c in range(n):
        if c == bernice:
            model.add_constr(child_story[c][passover] == 0)
        else:
            implies_difference(child_story[c][passover], age(c) - age(bernice), 2)

    # The child from the Yemeni family is younger than the child from the Ethiopian family.
    for c in range(n):
        for d in range(n):
            if c != d:
                yemeni_and_ethiopian = child_country[c][yemen] + child_country[d][ethiopia]  # 2 when both hold
                model.add_constr(age(c) - age(d) + 1 <= big_m * (2 - yemeni_and_ethiopian))

    # The child from the Moroccan family is three years older than Ted, so Ted is not
    # from that family.
    for c in range(n):
        if c == ted:
            model.add_constr(child_country[c][morocco] == 0)
        else:
            implies_difference(child_country[c][morocco], age(c) - age(ted), 3)

    # Sammy is three years older than the child who told of Moses's youth in the house
    # of the Pharaoh, so Sammy did not tell that story.
    for c in range(n):
        if c == sammy:
            model.add_constr(child_story[c][moses_youth] == 0)
        else:
            implies_difference(child_story[c][moses_youth], age(sammy) - age(c), 3)

    # The group number of each age, child, country and story.
    return model, {
        "ages": [group_number("age", e) for e in range(n)],
        "children": [group_number("child", e) for e in range(n)],
        "countries": [group_number("country", e) for e in range(n)],
        "stories": [group_number("story", e) for e in range(n)],
    }


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
