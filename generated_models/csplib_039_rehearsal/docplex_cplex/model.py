# csplib_039_rehearsal: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

from docplex.mp.model import Model


def create_model(instance):
    """Rehearsal scheduling: put the pieces of a concert in a rehearsal order. Each player arrives
    for the first piece they play in and leaves after the last one, and waits through every piece
    in between that they do not play in. Minimise the total waiting time, counted in the
    durations of the pieces waited through."""
    num_pieces = instance["num_pieces"]    # number of pieces, and of rehearsal slots
    num_players = instance["num_players"]  # number of players
    duration = instance["duration"]        # duration[q]: length of piece q
    rehearsal = instance["rehearsal"]      # rehearsal[p][q] = 1 when player p plays in piece q

    pieces = range(num_pieces)
    slots = range(num_pieces)
    players = range(num_players)

    model = Model("rehearsal")

    # at[q, i] is 1 when piece q is rehearsed in slot i. Each piece is rehearsed exactly once,
    # and each slot holds one piece, so the order is a permutation.
    at = model.binary_var_matrix(pieces, slots, name="at")
    model.add_constraints(model.sum(at[q, i] for i in slots) == 1 for q in pieces)
    model.add_constraints(model.sum(at[q, i] for q in pieces) == 1 for i in slots)

    # rehearsal_order[i] is the piece rehearsed in the i-th slot.
    rehearsal_order = [model.sum(q * at[q, i] for q in pieces) for i in slots]

    waiting = []
    for p in players:
        # plays[i] is 1 when player p plays in the piece of slot i.
        plays = [model.sum(at[q, i] for q in pieces if rehearsal[p][q] == 1) for i in slots]

        # arrived[i] is 1 when player p has arrived by slot i, and staying[i] is 1 when player
        # p has not yet left at slot i. A player must be present for all pieces they play in:
        # once arrived they stay arrived, and they stay until their last piece.
        arrived = [model.binary_var(name=f"arrived_{p}_{i}") for i in slots]
        staying = [model.binary_var(name=f"staying_{p}_{i}") for i in slots]
        for i in slots:
            model.add_constraint(arrived[i] >= plays[i])
            model.add_constraint(staying[i] >= plays[i])
            if i > 0:
                model.add_constraint(arrived[i] >= arrived[i - 1])
                model.add_constraint(staying[i - 1] >= staying[i])

        # A player waits through a piece they do not play in when it falls in a slot where they
        # are present (arrived and not yet left). waits is 1 when player p waits through
        # piece q; it costs the duration of the piece. The constraint below forces it to 1 when
        # piece q is in slot i and player p is both arrived and staying there (the three terms
        # add up to 3).
        for q in pieces:
            if rehearsal[p][q] == 1:
                continue
            waits = model.binary_var(name=f"waits_{p}_{q}")
            for i in slots:
                model.add_constraint(waits >= at[q, i] + arrived[i] + staying[i] - 2)
            waiting.append(duration[q] * waits)

    # Minimise the total time that players are present but not playing.
    model.minimize(model.sum(waiting))

    return model, {"rehearsal_order": rehearsal_order}


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
