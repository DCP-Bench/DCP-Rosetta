# csplib_039_rehearsal: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, Iff, Or, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """A concert consists of pieces of different durations, each played by a different combination
    of orchestra members. A player arrives just before the first piece they play in and leaves
    just after the last. Order the pieces for rehearsal so that the total time players spend
    present but not playing is as small as possible."""
    n_pieces = instance["num_pieces"]    # the number of pieces
    n_players = instance["num_players"]  # the number of players
    duration = instance["duration"]      # duration[j]: the length of piece j
    rehearsal = instance["rehearsal"]    # rehearsal[p][j]: 1 when player p plays in piece j
    slots = range(n_pieces)              # the rehearsal slots, in order

    # in_slot[j][s] is true when piece j is rehearsed in slot s
    in_slot = [[Bool(f"in_slot_{j}_{s}") for s in slots] for j in range(n_pieces)]

    # True when at least one of the conditions holds.
    def any_of(conditions):
        return conditions[0] if len(conditions) == 1 else Or(conditions)

    # The constraints of the model, collected as they are added.
    constraints = []

    # Each piece is rehearsed in exactly one slot.
    for j in range(n_pieces):
        constraints.append(sum(in_slot[j][s] for s in slots) == 1)

    # Each slot rehearses exactly one piece.
    for s in slots:
        constraints.append(sum(in_slot[j][s] for j in range(n_pieces)) == 1)

    # The waiting time of each player in each slot, as terms of the total waiting time.
    waiting_time = []

    for p in range(n_players):
        pieces = [j for j in range(n_pieces) if rehearsal[p][j]]

        # Player p plays in a slot when the piece rehearsed there is one of their pieces.
        # A player with no pieces never plays.
        playing = []
        for s in slots:
            plays = Bool(f"plays_{p}_{s}")
            if pieces:
                constraints.append(Iff(plays, any_of([in_slot[j][s] for j in pieces])))
            else:
                constraints.append(~plays)
            playing.append(plays)

        # arrived[s] is true when player p has arrived by slot s, which is just before the first
        # piece they play in.
        arrived = []
        for s in slots:
            a = Bool(f"arrived_{p}_{s}")
            prev = playing[s] if s == 0 else (arrived[s - 1] | playing[s])
            constraints.append(Iff(a, prev))
            arrived.append(a)

        # still_needed[s] is true when player p plays in slot s or in a later slot, so they stay
        # until just after their last piece.
        still_needed = [None] * n_pieces
        for s in reversed(slots):
            needed = Bool(f"still_needed_{p}_{s}")
            later = playing[s] if s == n_pieces - 1 else (playing[s] | still_needed[s + 1])
            constraints.append(Iff(needed, later))
            still_needed[s] = needed

        # Player p waits in slot s when they are present, that is arrived and still needed, and not
        # playing. The waiting time is the duration of the piece rehearsed in that slot.
        for s in slots:
            waits = Bool(f"waits_{p}_{s}")
            constraints.append(Iff(waits, arrived[s] & still_needed[s] & ~playing[s]))
            for j in range(n_pieces):
                a = Bool(f"waits_{p}_{s}_{j}")
                constraints.append(Iff(a, waits & in_slot[j][s]))
                waiting_time.append(duration[j] * a)

    # The total waiting time of all players, to minimise.
    total_waiting = sum(waiting_time)

    # The piece rehearsed in each slot, in order.
    rehearsal_order = [sum(j * in_slot[j][s] for j in range(n_pieces)) for s in slots]

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_waiting, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the total waiting time of the players,
    # minimised (its negation is what the soft clauses maximise).
    return (formula, pool), {"rehearsal_order": rehearsal_order}, total_waiting


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs, objective = create_model(instances[index])

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
        print("objective =", evaluate(objective, truth))
    else:
        print("No solution")
