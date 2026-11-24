# session2_movie_scheduling: a CPLEX (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python session2_movie_scheduling.py session2_movie_scheduling.json

from docplex.mp.model import Model


def create_model(instance):
    """Accept the largest possible set of movie offers, all paying the same fee, such that no two of
    them have overlapping filming periods (first to last day of filming)."""
    movies = instance["movies"]  # movies[i]: [title, first day, last day of filming]
    n = len(movies)
    first_day = [movie[1] for movie in movies]  # first_day[i]: first day of filming of movie i
    last_day = [movie[2] for movie in movies]   # last_day[i]: last day of filming of movie i

    model = Model("movie_scheduling")

    # selected[i] is 1 when the offer for movie i is accepted, and 0 when not
    selected = model.binary_var_list(n, name="selected_movies")

    # Two films whose filming periods overlap, sharing even one day, cannot both be accepted.
    for i in range(n):
        for j in range(i + 1, n):
            if last_day[i] >= first_day[j] and last_day[j] >= first_day[i]:
                model.add_constraint(selected[i] + selected[j] <= 1, ctname=f"overlap_{i}_{j}")

    # Maximise the number of films accepted.
    model.maximize(model.sum(selected))

    return model, {"selected_movies": selected}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
