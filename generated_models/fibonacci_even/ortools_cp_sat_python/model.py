# fibonacci_even: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install ortools`) with:
#   python fibonacci_even.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Each new term in the Fibonacci sequence is the sum of the previous two.
    Starting from 1 and 2, find the sum of the even-valued terms that do not
    exceed four million."""
    n_terms = 35        # enough terms to pass four million
    cutoff = 4_000_000  # terms must not exceed this
    upper = 10_000_000  # bound on every term, well above the cutoff

    model = cp_model.CpModel()

    # f[i] is the i-th Fibonacci number; the puzzle's terms 1, 2, 3, 5, ... are f[2], f[3], f[4], f[5], ...
    f = [model.new_int_var(0, upper, f"f_{i}") for i in range(n_terms + 1)]
    # counted[i] is true when term i is counted in the answer
    counted = [model.new_bool_var(f"counted_{i}") for i in range(n_terms + 1)]
    # res is the answer to the puzzle
    res = model.new_int_var(0, 100_000_000, "res")

    # The sequence starts 0, 1, 1, and each later term is the sum of the previous two.
    model.add(f[0] == 0)
    model.add(f[1] == 1)
    model.add(f[2] == 1)
    for i in range(3, n_terms + 1):
        model.add(f[i] == f[i - 1] + f[i - 2])

    # Term 0 is 0, which adds nothing, so it is never counted.
    model.add(counted[0] == 0)

    # contributions lists what each term adds to the answer
    contributions = []
    for i in range(1, n_terms + 1):
        # remainder is the remainder of term i after dividing by 2
        remainder = model.new_int_var(0, 1, f"remainder_{i}")
        model.add_modulo_equality(remainder, f[i], 2)
        # is_even is true when term i is even, that is, when its remainder is 0
        is_even = model.new_bool_var(f"is_even_{i}")
        model.add(remainder == 0).only_enforce_if(is_even)
        model.add(remainder == 1).only_enforce_if(~is_even)

        # is_small is true when term i does not exceed the cutoff
        is_small = model.new_bool_var(f"is_small_{i}")
        model.add(f[i] <= cutoff).only_enforce_if(is_small)
        model.add(f[i] > cutoff).only_enforce_if(~is_small)

        # Term i is counted exactly when it is even and does not exceed the cutoff.
        model.add_bool_and([is_even, is_small]).only_enforce_if(counted[i])
        model.add_bool_or([~is_even, ~is_small]).only_enforce_if(~counted[i])

        # contribution is the term when it is counted, and 0 otherwise
        contribution = model.new_int_var(0, upper, f"contribution_{i}")
        model.add(contribution == f[i]).only_enforce_if(counted[i])
        model.add(contribution == 0).only_enforce_if(~counted[i])
        contributions.append(contribution)

    # The answer is the sum of the contributions.
    model.add(res == sum(contributions))

    return model, {"res": res}


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
