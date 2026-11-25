# initials_queue: a FOX model for GroundFOX from DCP Rosetta.
#
# I noticed something weird about names of the first 10 people in the queue for a Maths
# lecture.
#
# Each of them had initials which were an alphabetically ordered pair of distinct letters from
# the first five letters of the alphabet (A,B,C,D,E)! None of the people had the same initials
# as any other and no-one shared a letter with the person in front of them. Mathematician BE
# was at the front of the queue with CD right behind, while BD was right at the end of the
# queue. Can you use this information to work out the initials of the ten people in the queue,
# starting from the front?
#
# Print the queue (queue) of the initials as a list of 10 lists of 2 integers ranging from 0
# to 4, representing A to E.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py initials_queue.json --check

"""initials_queue: a FOX model for GroundFOX from DCP Rosetta.

queue(p, k, v): person p (0-based, front of queue is 0) has letter v (0=A .. 4=E) at
position k (0 = first initial, 1 = second). Initials are ordered pairs a < b.
"""

FOX = """
invocabulary { Person/1 Letter/1 Pos/1 Next/2 NoLt/2 }
outvocabulary { queue/3 }
theory {
    ! p [Person(p)] : ! k [Pos(k)] : ? v [Letter(v)] : queue(p, k, v).
    ! p [Person(p)] : ! k [Pos(k)] : ! v [Letter(v)] : ! w [Letter(w) & v ~= w] : ~queue(p, k, v) | ~queue(p, k, w).
    ! p [Person(p)] : ! a [Letter(a)] : ! b [NoLt(a, b)] : ~queue(p, 0, a) | ~queue(p, 1, b).
    ! p [Person(p)] : ! q [Person(q) & p ~= q] : ! a [Letter(a)] : ! b [Letter(b)] : ~queue(p, 0, a) | ~queue(p, 1, b) | ~queue(q, 0, a) | ~queue(q, 1, b).
    ! p [Person(p)] : ! q [Next(p, q)] : ! k [Pos(k)] : ! l [Pos(l)] : ! v [Letter(v)] : ~queue(p, k, v) | ~queue(q, l, v).
    ! u [u = 0] : queue(0, 0, 1).
    ! u [u = 0] : queue(0, 1, 4).
    ! u [u = 1] : queue(1, 0, 2).
    ! u [u = 1] : queue(1, 1, 3).
    ! u [u = 9] : queue(9, 0, 1).
    ! u [u = 9] : queue(9, 1, 3).
}
"""


def structure(instance):
    n = 10
    return {
        "Person": range(n),
        "Letter": range(5),
        "Pos": range(2),
        "Next": [(p, p + 1) for p in range(n - 1)],
        "NoLt": [(a, b) for a in range(5) for b in range(5) if not a < b],
    }
