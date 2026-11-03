# session2_movie_scheduling: a Paramita (Python) model from DCP Rosetta.
# Download the `session2_movie_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python session2_movie_scheduling.py session2_movie_scheduling.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """An actor is offered movie projects, each with a first and last day of
    filming. Two projects whose filming periods overlap cannot both be accepted:
    accept as many projects as possible."""
    movies = instance["movies"]  # movies[i]: [title, first day, last day] of the i-th movie
    n_movies = len(movies)       # the number of movie offers

    starts = [movie[1] for movie in movies]  # starts[i]: the first day of filming of movie i
    ends = [movie[2] for movie in movies]    # ends[i]: the last day of filming of movie i

    # selected[i] is true when the actor accepts movie i
    selected = [Bool(f"selected_{i}") for i in range(n_movies)]

    # Two movies cannot both be accepted when their filming periods share a day.
    subject_to = []
    for i in range(n_movies):
        for j in range(i + 1, n_movies):
            if starts[i] <= ends[j] and starts[j] <= ends[i]:
                subject_to.append(~(selected[i] & selected[j]))

    # Accept as many movies as possible, since every film pays the same fee.
    accepted = sum(selected)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(accepted, And(subject_to), to_cnf, formula, pool)

    return (formula, pool), {"selected_movies": selected}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
