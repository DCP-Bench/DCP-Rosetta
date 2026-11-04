# session3_exodus: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session3_exodus.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Five children at Hebrew school (Bernice, Carl, Debby, Sammy and Ted) each
    tell one part of the Exodus story. Each is a different age, and each family
    came to America from a different country. Find each child's age, family
    country and story from the clues."""
    n_children = 5

    age_years = [3, 5, 7, 8, 10]           # the possible ages of the children, in years
    countries = ["Ethiopia", "Kazakhstan", "Lithuania", "Morocco", "Yemen"]
    stories = ["burning bush", "captivity", "Moses's youth", "Passover", "Ten Commandments"]

    # The children, countries and stories are numbered from 0 in the order the problem lists them.
    bernice, carl, debby, sammy, ted = range(5)
    ethiopia, kazakhstan, lithuania, morocco, yemen = range(5)
    burning_bush, captivity, moses_youth, passover, ten_commandments = range(5)

    # age[c][v] is true when child c is aged age_years[v]
    age = [[Bool(f"age_{c}_{v}") for v in range(n_children)] for c in range(n_children)]
    # country[c][v] is true when child c comes from countries[v]
    country = [[Bool(f"country_{c}_{v}") for v in range(n_children)] for c in range(n_children)]
    # story[c][v] is true when child c tells the story stories[v]
    story = [[Bool(f"story_{c}_{v}") for v in range(n_children)] for c in range(n_children)]

    # years[c] is the age of child c in years
    years = [sum(age_years[v] * age[c][v] for v in range(n_children)) for c in range(n_children)]

    subject_to = []

    # Each child has exactly one age, one family country and one story.
    for c in range(n_children):
        subject_to.append(sum(age[c]) == 1)
        subject_to.append(sum(country[c]) == 1)
        subject_to.append(sum(story[c]) == 1)

    # Each age, each country and each story belongs to exactly one child.
    for v in range(n_children):
        subject_to.append(sum(age[c][v] for c in range(n_children)) == 1)
        subject_to.append(sum(country[c][v] for c in range(n_children)) == 1)
        subject_to.append(sum(story[c][v] for c in range(n_children)) == 1)

    # Debby's family is from Lithuania.
    subject_to.append(country[debby][lithuania])

    # The child who told the story of the Passover is two years older than Bernice.
    for c in range(n_children):
        subject_to.append(If(story[c][passover], years[c] == years[bernice] + 2))

    # The child whose family is from Yemen is younger than the child from the Ethiopian family.
    for c in range(n_children):
        for d in range(n_children):
            if c != d:
                subject_to.append(If(country[c][yemen] & country[d][ethiopia], years[c] < years[d]))

    # The child from the Moroccan family is three years older than Ted.
    for c in range(n_children):
        subject_to.append(If(country[c][morocco], years[c] == years[ted] + 3))

    # Sammy is three years older than the child who told the story of Moses's youth.
    for c in range(n_children):
        subject_to.append(If(story[c][moses_youth], years[sammy] == years[c] + 3))

    # The children are numbered 1 to 5, and each output lists the number of the child
    # that holds each value.
    ages = [sum((c + 1) * age[c][v] for c in range(n_children)) for v in range(n_children)]
    countries_out = [sum((c + 1) * country[c][v] for c in range(n_children)) for v in range(n_children)]
    stories_out = [sum((c + 1) * story[c][v] for c in range(n_children)) for v in range(n_children)]
    children = [c + 1 for c in range(n_children)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {
        "ages": ages,
        "children": children,
        "countries": countries_out,
        "stories": stories_out,
    }


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
