# session3_exodus: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install pychoco numpy`) with:
#   python session3_exodus.py

from pychoco.model import Model


def create_model(instance):
    """Five children at Hebrew school (Bernice, Carl, Debby, Sammy and Ted) each
    told one part of the Exodus story. Each child is a different age, and each
    family came to America from a different country. Find every child's age,
    family country and story from the clues."""
    age_values = [3, 5, 7, 8, 10]  # the possible ages of the children, in years
    n_children = len(age_values)   # the number of children

    model = Model()

    def group(category):
        """One number from 1 to n_children for each entity of the category.
        Entities with the same number belong to the same child."""
        return [model.intvar(1, n_children, name=f"{category}_{k}") for k in range(n_children)]

    # ages[k]: the number of the child who is age_values[k] years old
    ages = group("age")
    # children[k]: the number of the k-th child named in the puzzle
    children = group("child")
    bernice, carl, debby, sammy, ted = children
    # countries[k]: the number of the child whose family came from the k-th country
    countries = group("country")
    ethiopia, kazakhstan, lithuania, morocco, yemen = countries
    # stories[k]: the number of the child who told the k-th part of the story
    stories = group("story")
    burning_bush, captivity, moses_youth, passover, ten_commandments = stories

    # Within each category, every child has a different value.
    for category in (ages, children, countries, stories):
        model.all_different(category).post()

    def age_of(child, name):
        """The age of the child with the number `child`. `name` labels the variables."""
        slot = model.intvar(0, n_children - 1, name=f"slot_{name}")
        model.element(child, ages, slot).post()
        age = model.intvar(min(age_values), max(age_values), name=f"age_{name}")
        model.element(age, age_values, slot).post()
        return age

    # Debby's family is from Lithuania.
    model.arithm(debby, "=", lithuania).post()
    # The child who told the Passover story is two years older than Bernice.
    model.arithm(age_of(passover, "passover"), "-", age_of(bernice, "bernice"), "=", 2).post()
    # The child whose family is from Yemen is younger than the child from the Ethiopian family.
    model.arithm(age_of(yemen, "yemen"), "<", age_of(ethiopia, "ethiopia")).post()
    # The child from the Moroccan family is three years older than Ted.
    model.arithm(age_of(morocco, "morocco"), "-", age_of(ted, "ted"), "=", 3).post()
    # Sammy is three years older than the child who told the story of Moses's youth.
    model.arithm(age_of(sammy, "sammy"), "-", age_of(moses_youth, "moses_youth"), "=", 3).post()

    return model, {"ages": ages, "children": children, "countries": countries, "stories": stories}, None


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
