# csplib_026_sports_tournament_scheduling: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

from hermax.model import Model


def create_model(instance):
    """Sports tournament scheduling: n teams play every other team exactly once, over
    n-1 weeks, each week split into n/2 periods of two slots (home team, away team).
    Every team plays once a week, and plays at most twice in the same period over the
    whole tournament. Find the home and away schedules."""
    n = instance["n_teams"]     # the number of teams, numbered 1..n in the output
    weeks = n - 1               # the tournament lasts n-1 weeks
    periods = n // 2            # each week has n/2 periods, each with a home and an away slot

    m = Model()

    # home[w][p] is the team playing at home in week w, period p (teams numbered 1..n)
    home = m.int_matrix("home", weeks, periods, 1, n)
    # away[w][p] is the team playing away in week w, period p
    away = m.int_matrix("away", weeks, periods, 1, n)

    # Every team plays once a week: the n slots of a week hold each team exactly once.
    for w in range(weeks):
        week_slots = [home[w][p] for p in range(periods)] + [away[w][p] for p in range(periods)]
        m &= m.vector(week_slots).all_different()

    # Every team plays at most twice in the same period over the whole tournament.
    for t in range(1, n + 1):
        for p in range(periods):
            m &= (sum([(home[w][p] == t) for w in range(weeks)]
                      + [(away[w][p] == t) for w in range(weeks)]) <= 2)

    # Every team plays every other team exactly once: each pair of teams (i, j) meets in
    # exactly one slot, either with i at home or with j at home. Each orientation gets a
    # Boolean z reified as "x is home and y is away" in that slot; the pair meets once
    # when the z over all weeks and periods sum to one.
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            meetings = []
            for w in range(weeks):
                for p in range(periods):
                    for x, y in ((i, j), (j, i)):
                        z = m.bool()
                        m &= ((home[w][p] == x) & (away[w][p] == y)).iff(z)
                        meetings.append(z)
            m &= (sum(meetings) == 1)

    return m, {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
