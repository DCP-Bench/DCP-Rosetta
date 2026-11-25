# appointment_scheduling: a FOX model for GroundFOX from DCP Rosetta.
#
# Schedule 4 people into 4 interview slots based on their free-busy schedules, where `m[i][j]`
# is 1 if person i is free in slot j. Each person gets exactly one slot in which they are
# free, and each slot goes to exactly one person.
#
# Print the assignment of people to slots (x) as a list of lists of booleans, where x[i][j] is
# True if person i is assigned to slot j, and False otherwise.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py appointment_scheduling.json --check

# appointment_scheduling: a FOX model for GroundFOX from DCP Rosetta.
#
# Assign each of the people to exactly one interview slot in which they are free,
# and each slot to exactly one person. x[i][j] is 1 iff person i gets slot j.

FOX = """
invocabulary { Person/1 Slot/1 Bit/1 Free/2 }
outvocabulary { x/3 }
theory {
    ! i [Person(i)] : ! j [Slot(j)] : ? b [Bit(b)] : x(i, j, b).
    ! i [Person(i)] : ! j [Slot(j)] : ! b [Bit(b)] : ! c [Bit(c) & b ~= c] : ~x(i, j, b) | ~x(i, j, c).
    ! i [Person(i)] : ! j [Slot(j) & ~Free(i, j)] : ~x(i, j, 1).
    ! i [Person(i)] : ? j [Slot(j)] : x(i, j, 1).
    ! i [Person(i)] : ! j [Slot(j)] : ! k [Slot(k) & j ~= k] : ~x(i, j, 1) | ~x(i, k, 1).
    ! j [Slot(j)] : ? i [Person(i)] : x(i, j, 1).
    ! j [Slot(j)] : ! i [Person(i)] : ! k [Person(k) & i ~= k] : ~x(i, j, 1) | ~x(k, j, 1).
}
"""


def structure(instance):
    m = instance["m"]
    rows = len(m)
    cols = len(m[0]) if rows else 0
    free = [(i, j) for i in range(rows) for j in range(cols) if m[i][j] == 1]
    return {
        "Person": list(range(rows)),
        "Slot": list(range(cols)),
        "Bit": [0, 1],
        "Free": free,
    }
