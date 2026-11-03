"""Best host: seat six guests round a table so that as few neighbouring pairs as possible would conflict."""
import hexaly.optimizer as hx

# Guests: 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank. Each will only sit next to the two listed
# (from the problem statement).
GETS_ALONG = {0: (3, 5), 1: (2, 4), 2: (1, 5), 3: (0, 4), 4: (1, 3), 5: (0, 2)}


def build(instance):
    n = 6
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] is the guest in seat i: a full list decision, the seats forming a circle
    seating = model.list(n)
    model.constraint(model.count(seating) == n)
    x = [seating[i] for i in range(n)]

    # fine[a][b] = 1 if guest a is happy to sit next to guest b
    fine = model.array([[1 if b in GETS_ALONG[a] else 0 for b in range(n)] for a in range(n)])
    # A conflict is a pair of neighbours (seat 5 is next to seat 0) who do not get along
    conflicts = [1 - model.at(fine, x[i], x[(i + 1) % n]) for i in range(n)]

    # Minimise the conflicts at dinner
    model.minimize(model.sum(conflicts))
    return optimizer, {"x": x}
