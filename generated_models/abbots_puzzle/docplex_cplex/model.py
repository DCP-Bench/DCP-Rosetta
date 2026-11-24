# abbots_puzzle: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python abbots_puzzle.py

from docplex.mp.model import Model


def create_model(instance):
    """Abbot's puzzle: 100 bushels of corn are shared among 100 people, each man getting three bushels,
    each woman two and each child half a bushel, with five times as many women as men. How many men,
    women and children are there?"""
    people = 100   # people sharing the corn (puzzle constant)
    bushels = 100  # bushels of corn shared (puzzle constant)

    model = Model("abbots_puzzle")

    # The number of men, women and children; none can number more than all the people.
    men = model.integer_var(0, people, name="men")
    women = model.integer_var(0, people, name="women")
    children = model.integer_var(0, people, name="children")

    # Together the men, women and children make up all the people.
    model.add_constraint(men + women + children == people)

    # They receive 100 bushels: 3 per man, 2 per woman, 1/2 per child (doubled to stay integral).
    model.add_constraint(6 * men + 4 * women + children == 2 * bushels)

    # There are five times as many women as men.
    model.add_constraint(5 * men == women)

    return model, {"men": men, "women": women, "children": children}


if __name__ == "__main__":
    model, outputs = create_model({})
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
