# csplib_039_rehearsal: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A concert consists of pieces of different durations, each played by a different combination
    of orchestra members. A player arrives just before the first piece they play in and leaves
    just after the last. Order the pieces for rehearsal so that the total time players spend
    present but not playing is as small as possible."""
    n_pieces = instance["num_pieces"]    # the number of pieces
    n_players = instance["num_players"]  # the number of players
    duration = instance["duration"]      # duration[q]: the rehearsal time of piece q
    rehearsal = instance["rehearsal"]    # rehearsal[p][q]: whether player p plays in piece q

    model = cp_model.CpModel()

    # rehearsal_order[i] is the piece rehearsed in slot i
    rehearsal_order = [model.new_int_var(0, n_pieces - 1, f"order_{i}") for i in range(n_pieces)]
    # arrival[p] is the first slot in which player p is present, departure[p] the last
    arrival = [model.new_int_var(0, n_pieces - 1, f"arrival_{p}") for p in range(n_players)]
    departure = [model.new_int_var(0, n_pieces - 1, f"departure_{p}") for p in range(n_players)]

    # slot_duration[i] is the length of the piece rehearsed in slot i
    # plays[p][i] is true when player p plays in the piece rehearsed in slot i
    slot_duration = []
    plays = [[None] * n_pieces for _ in range(n_players)]
    for i in range(n_pieces):
        slot_duration.append(model.new_int_var(min(duration), max(duration), f"slot_duration_{i}"))
        model.add_element(rehearsal_order[i], duration, slot_duration[i])
        for p in range(n_players):
            plays[p][i] = model.new_bool_var(f"plays_{p}_{i}")
            model.add_element(rehearsal_order[i], rehearsal[p], plays[p][i])

    # Every piece is rehearsed exactly once.
    model.add_all_different(rehearsal_order)

    # waiting holds the time each player waits in each slot.
    waiting = []
    for p in range(n_players):
        for i in range(n_pieces):
            # A player is present in every slot in which they play.
            model.add(arrival[p] <= i).only_enforce_if(plays[p][i])
            model.add(departure[p] >= i).only_enforce_if(plays[p][i])

            # Player p is present in slot i when they have arrived by slot i and have not left yet.
            arrived = model.new_bool_var(f"arrived_{p}_{i}")
            model.add(arrival[p] <= i).only_enforce_if(arrived)
            model.add(arrival[p] > i).only_enforce_if(~arrived)
            not_left = model.new_bool_var(f"not_left_{p}_{i}")
            model.add(departure[p] >= i).only_enforce_if(not_left)
            model.add(departure[p] < i).only_enforce_if(~not_left)

            # wait is true when player p is present in slot i but not playing.
            wait = model.new_bool_var(f"wait_{p}_{i}")
            model.add_bool_and([arrived, not_left, ~plays[p][i]]).only_enforce_if(wait)
            model.add_bool_or([~arrived, ~not_left, plays[p][i]]).only_enforce_if(~wait)
            # wait_time is the length of slot i when player p waits in it, and 0 otherwise.
            wait_time = model.new_int_var(0, max(duration), f"wait_time_{p}_{i}")
            model.add_multiplication_equality(wait_time, [slot_duration[i], wait])
            waiting.append(wait_time)

    # Minimise the total time that players spend waiting.
    model.minimize(sum(waiting))

    return model, {"rehearsal_order": rehearsal_order}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
