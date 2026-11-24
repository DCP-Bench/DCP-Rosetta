# chess_set: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python chess_set.py

from docplex.mp.model import Model


def create_model(instance):
    """Chess sets: a joinery makes small and large chess sets, limited by 160 lathe-hours and 200 kg of
    boxwood per week; choose how many of each to make to maximize profit."""
    small_hours, large_hours = 3, 2     # lathe-hours to machine one small / one large set
    lathe_hours = 4 * 40                # four lathes, each worked 40 hours a week
    small_wood, large_wood = 1, 3       # kg of boxwood in one small / one large set
    boxwood = 200                       # kg of boxwood that can be obtained per week
    small_profit, large_profit = 5, 20  # dollars of profit from selling one small / one large set

    model = Model("chess_set")

    # The number of small and of large sets made each week (whole sets, at least 0; the two
    # limits below keep them finite).
    small_set = model.integer_var(name="small_set")
    large_set = model.integer_var(name="large_set")

    # The machining stays within the lathe-hours available.
    model.add_constraint(small_hours * small_set + large_hours * large_set <= lathe_hours)

    # The boxwood used stays within what can be obtained.
    model.add_constraint(small_wood * small_set + large_wood * large_set <= boxwood)

    # The weekly profit, to be maximized.
    max_profit = small_profit * small_set + large_profit * large_set
    model.maximize(max_profit)

    return model, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}


if __name__ == "__main__":
    model, outputs = create_model({})
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
