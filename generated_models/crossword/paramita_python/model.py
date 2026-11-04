# crossword: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python crossword.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def find_slots(grid):
    """The across and down word slots of a grid: each run of two or more white cells.
    A slot is a dict with the number of its first cell (None if unnumbered) and its
    cells as (row, column) pairs."""
    rows, cols = len(grid), len(grid[0])
    slots = []  # the slots found so far
    for r in range(rows):
        c = 0
        while c < cols:
            if grid[r][c] == "#":
                c += 1
                continue
            start = c
            while c < cols and grid[r][c] != "#":
                c += 1
            if c - start >= 2:
                slots.append({"number": int(grid[r][start]) if grid[r][start].isdigit() else None,
                              "cells": [(r, k) for k in range(start, c)]})
    for c in range(cols):
        r = 0
        while r < rows:
            if grid[r][c] == "#":
                r += 1
                continue
            start = r
            while r < rows and grid[r][c] != "#":
                r += 1
            if r - start >= 2:
                slots.append({"number": int(grid[start][c]) if grid[start][c].isdigit() else None,
                              "cells": [(k, c) for k in range(start, r)]})
    return slots


def create_model(instance):
    """Complete a crossword grid with 8 words chosen from a list of 15, so that where two
    words cross they share the same letter."""
    # '#' marks a black cell; the digits 1 to 8 mark the cells where numbered words start.
    grid = [
        "1.2.3",
        "##.#.",
        "#4.5.",
        "6#7..",
        "8....",
        ".##.#",
    ]
    # The 15 words to choose from, longest first, then alphabetically.
    words = [
        "HOSES", "LASER", "SAILS", "SHEET", "STEER",
        "HEEL", "HIKE", "KEEL", "KNOT", "LINE",
        "AFT", "ALE", "EEL", "LEE", "TIE",
    ]
    n_words = len(words)

    # The word slots, in the order of their numbers 1 to 8.
    slots = sorted(find_slots(grid), key=lambda s: s["number"])

    # fills[k][j] is true when word j fills slot k
    fills = [[Bool(f"fills_{k}_{j}") for j in range(n_words)] for k in range(len(slots))]

    constraints = []  # the constraints of the puzzle, collected below
    # Each slot holds exactly one word, and that word has the length of the slot.
    for k, slot in enumerate(slots):
        constraints.append(sum(fills[k]) == 1)
        for j, word in enumerate(words):
            if len(word) != len(slot["cells"]):
                constraints.append(~fills[k][j])

    # Each word fills at most one slot, so the eight words are different.
    for j in range(n_words):
        constraints.append(sum(fills[k][j] for k in range(len(slots))) <= 1)

    # owners[cell]: the (slot, position in the word) pairs for the slots that use that cell
    owners = {}
    for k, slot in enumerate(slots):
        for pos, cell in enumerate(slot["cells"]):
            owners.setdefault(cell, []).append((k, pos))
    # Where two words cross, they have the same letter in the shared cell.
    for uses in owners.values():
        if len(uses) < 2:
            continue
        (a, pos_a), (b, pos_b) = uses
        for u, word_u in enumerate(words):
            if pos_a >= len(word_u):
                continue
            for v, word_v in enumerate(words):
                if pos_b >= len(word_v):
                    continue
                if word_u[pos_a] != word_v[pos_b]:
                    constraints.append(~(fills[a][u] & fills[b][v]))

    # E[k] is the number of the word that fills slot k, counting from 0 in the list above.
    E = [sum(j * fills[k][j] for j in range(n_words)) for k in range(len(slots))]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"E": E}


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
