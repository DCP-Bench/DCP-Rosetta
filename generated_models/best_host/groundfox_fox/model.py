# best_host: a FOX model for GroundFOX from DCP Rosetta.
#
# Hosting a dinner party requires several skills to pull off a successful evening. One of your
# duties, aside from preparing dinner and selecting the drinks, is to make sure your guests
# enjoy themselves.
#
# Figure 1 shows a dinner table with six seats for your guests. Some guests, however, do not
# get along with each other. If two guests who do not get along are seated next to each other,
# it will create conflict at dinner. As host, you must arrange the guests in a seating order
# that minimizes conflict.
#
# Andrew will only sit next to Dave and Frank; Betty will only sit next to Cara and Erica;
# Cara will only sit next to Betty and Frank; Dave will only sit next to Andrew and Erica;
# Erica will only sit next to Betty and Dave; Frank will only sit next to Andrew and Cara.
#
# Figure 1 shows the following arrangement:
#
# ```text Andrew Frank Betty Erica Cara Dave ```
#
# In the example seating arrangement above, there are three conflicts (Andrew and Betty, Cara
# and Dave, Erica and Frank).
#
# Question:
#
# What seating arrangement will minimize the conflict at dinner? An arrangement without any
# conflict exists, so every guest must sit only next to the two guests they will sit next to.
#
# Print the list of guests (x) in the seating order going around the table, where 0 represents
# Andrew, 1 represents Betty, 2 represents Cara, 3 represents Dave, 4 represents Erica, and 5
# represents Frank.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py best_host.json --check

# best_host: a FOX model for GroundFOX from DCP Rosetta.
#
# Six guests sit around a round table; guests who do not get along must not be
# seated next to each other. Output x[seat] is the guest at that seat.

FOX = """
invocabulary { Seat/1 Guest/1 Next/2 Adj/2 }
outvocabulary { x/2 }
theory {
    ! i [Seat(i)] : ? g [Guest(g)] : x(i, g).
    ! i [Seat(i)] : ! g [Guest(g)] : ! h [Guest(h) & g ~= h] : ~x(i, g) | ~x(i, h).
    ! g [Guest(g)] : ! i [Seat(i)] : ! j [Seat(j) & i ~= j] : ~x(i, g) | ~x(j, g).
    ! i [Seat(i)] : ! j [Next(i, j)] : ! g [Guest(g)] : ! h [Guest(h) & ~Adj(g, h)] : ~x(i, g) | ~x(j, h).
}
"""


def structure(instance):
    seats = list(range(6))
    # Guests who will sit next to each other (0 Andrew, 1 Betty, 2 Cara,
    # 3 Dave, 4 Erica, 5 Frank); the relation is symmetric.
    pairs = [(0, 3), (0, 5), (1, 2), (1, 4), (2, 5), (3, 4)]
    adj = pairs + [(b, a) for a, b in pairs]
    nxt = [(i, (i + 1) % 6) for i in seats] + [((i + 1) % 6, i) for i in seats]
    return {"Seat": seats, "Guest": seats, "Next": nxt, "Adj": adj}
