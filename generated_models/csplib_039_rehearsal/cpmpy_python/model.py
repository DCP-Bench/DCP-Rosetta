# csplib_039_rehearsal: a CPMpy model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

import cpmpy as cp


def create_model(instance):
    """A concert consists of pieces of different durations, each played by a different combination
    of orchestra members. A player arrives just before the first piece they play in and leaves
    just after the last. Order the pieces for rehearsal so that the total time players spend
    present but not playing is as small as possible."""
    num_pieces = instance["num_pieces"]
    num_players = instance["num_players"]
    duration = cp.cpm_array(instance["duration"])  # duration[q]: the length of piece q
    plays = cp.cpm_array(instance["rehearsal"])    # plays[p][q] is 1 when player p plays in piece q

    # rehearsal_order[i] is the piece rehearsed in slot i
    rehearsal_order = cp.intvar(0, num_pieces - 1, shape=num_pieces, name="rehearsal_order")
    # arrival[p] is the first slot player p is present, departure[p] the last
    arrival = cp.intvar(0, num_pieces - 1, shape=num_players, name="arrival")
    departure = cp.intvar(0, num_pieces - 1, shape=num_players, name="departure")

    model = cp.Model()

    # Every piece is rehearsed once, so the order is a permutation of the pieces.
    model.add(cp.AllDifferent(rehearsal_order))

    # A player is present in every slot whose piece they play in: the slot lies between
    # their arrival and their departure.
    for p in range(num_players):
        for i in range(num_pieces):
            plays_in_slot = plays[p, rehearsal_order[i]] == 1
            model.add(plays_in_slot.implies((arrival[p] <= i) & (i <= departure[p])))

    # In each slot where a player is present but not playing, they wait for the whole duration
    # of the piece rehearsed in that slot.
    waiting_times = []
    for p in range(num_players):
        for i in range(num_pieces):
            present = (arrival[p] <= i) & (i <= departure[p])
            not_playing = plays[p, rehearsal_order[i]] == 0
            waiting_times.append(duration[rehearsal_order[i]] * (present & not_playing))

    # Minimise the total time players spend waiting.
    model.minimize(cp.sum(waiting_times))

    return model, {"rehearsal_order": rehearsal_order}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
