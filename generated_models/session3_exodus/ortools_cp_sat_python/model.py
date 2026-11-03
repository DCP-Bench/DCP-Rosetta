# session3_exodus: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install ortools`) with:
#   python session3_exodus.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Five children at Hebrew school (Bernice, Carl, Debby, Sammy and Ted) each
    tell one part of the Exodus story. Each is a different age (3, 5, 7, 8 or 10),
    and each family came to America from a different country: find each child's age,
    family country and story from the clues."""
    model = cp_model.CpModel()

    # The possible ages of the children, in years.
    age_values = [3, 5, 7, 8, 10]
    n_children = len(age_values)  # the number of children

    # ages[k]: the child aged age_values[k]
    ages = [model.new_int_var(1, n_children, f"age_{k}") for k in range(n_children)]
    # children[k]: the child called Bernice, Carl, Debby, Sammy and Ted, in that order
    children = [model.new_int_var(1, n_children, f"child_{k}") for k in range(n_children)]
    # countries[k]: the child from the k-th country, in order Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen
    countries = [model.new_int_var(1, n_children, f"country_{k}") for k in range(n_children)]
    # stories[k]: the child who tells the k-th story, in order burning bush, captivity, Moses's youth, Passover, Ten Commandments
    stories = [model.new_int_var(1, n_children, f"story_{k}") for k in range(n_children)]

    # Names for the children, countries and stories used in the clues.
    bernice, carl, debby, sammy, ted = children
    ethiopia, kazakhstan, lithuania, morocco, yemen = countries
    burning_bush, captivity, moses_youth, passover, ten_commandments = stories

    def same(variable, target, name):
        """Return a flag that is true exactly when `variable` is the child `target`."""
        flag = model.new_bool_var(name)
        model.add(variable == target).only_enforce_if(flag)
        model.add(variable != target).only_enforce_if(~flag)
        return flag

    def clue(child_a, child_b, holds, label):
        """Forbid every pair of ages that breaks a clue about two children.
        `holds(age_a, age_b)` says whether child_a aged age_a and child_b aged
        age_b satisfy the clue."""
        for i in range(n_children):
            for j in range(n_children):
                if holds(age_values[i], age_values[j]):
                    continue
                a_aged_i = same(ages[i], child_a, f"{label}_{i}_{j}_a")
                b_aged_j = same(ages[j], child_b, f"{label}_{i}_{j}_b")
                model.add_bool_or([~a_aged_i, ~b_aged_j])

    # Each age belongs to a different child.
    model.add_all_different(ages)
    # Each name belongs to a different child.
    model.add_all_different(children)
    # Each family country belongs to a different child.
    model.add_all_different(countries)
    # Each story belongs to a different child.
    model.add_all_different(stories)

    # Debby's family is from Lithuania.
    model.add(debby == lithuania)
    # The child who told of the Passover is two years older than Bernice.
    clue(passover, bernice, lambda a, b: a == b + 2, "passover")
    # The child from the Yemeni family is younger than the child from the Ethiopian family.
    clue(yemen, ethiopia, lambda a, b: a < b, "yemen")
    # The child from the Moroccan family is three years older than Ted.
    clue(morocco, ted, lambda a, b: a == b + 3, "morocco")
    # Sammy is three years older than the child who told of Moses's youth.
    clue(sammy, moses_youth, lambda a, b: a == b + 3, "sammy")

    return model, {
        "ages": ages,
        "children": children,
        "countries": countries,
        "stories": stories,
    }


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
