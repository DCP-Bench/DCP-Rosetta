# csplib_041_n_fractions: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_041_n_fractions.py

import itertools

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Or, add_to_container, to_cnf


def create_model(instance):
    """Find distinct non-zero digits A to I such that A / BC + D / EF + G / HI = 1, where BC, EF
    and HI are the two-digit numbers formed by B and C, E and F, and H and I."""
    # The problem fixes all its data, so nothing is read from the instance.
    digits = range(1, 10)
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

    # digit_is[n][v] is true when the letter n stands for the digit v
    digit_is = {n: {v: Bool(f"{n}_is_{v}") for v in digits} for n in letters}

    # Each letter stands for exactly one digit.
    constraints = [sum(digit_is[n].values()) == 1 for n in letters]

    # The nine letters stand for nine different digits, so each digit from 1 to 9 is used once.
    constraints += [sum(digit_is[n][v] for n in letters) == 1 for v in digits]

    # Multiplying A / BC + D / EF + G / HI = 1 by BC * EF * HI gives
    # A * EF * HI + D * BC * HI + G * BC * EF = BC * EF * HI. For each choice of digits for
    # B, C, E, F, A, D and G (the other two digits are H and I), this fixes HI. If no
    # two-digit HI works, the choice is ruled out. Otherwise H and I stand for its digits.
    for b, c, e, f, a, d, g in itertools.permutations(digits, 7):
        bc, ef = 10 * b + c, 10 * e + f
        # the choice is ruled out when a letter stands for another digit
        not_choice = [~digit_is["B"][b], ~digit_is["C"][c], ~digit_is["E"][e],
                      ~digit_is["F"][f], ~digit_is["A"][a], ~digit_is["D"][d],
                      ~digit_is["G"][g]]
        hi_num = g * bc * ef
        hi_den = bc * ef - a * ef - d * bc
        if hi_den <= 0 or hi_num % hi_den != 0:
            constraints.append(Or(not_choice))
            continue
        hi = hi_num // hi_den
        h, i = hi // 10, hi % 10
        if not (1 <= h <= 9 and 1 <= i <= 9):
            constraints.append(Or(not_choice))
            continue
        constraints.append(Or(not_choice + [digit_is["H"][h]]))
        constraints.append(Or(not_choice + [digit_is["I"][i]]))

    # The digit each letter stands for.
    outputs = {n: sum(v * digit_is[n][v] for v in digits) for n in letters}

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), outputs


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
