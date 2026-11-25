FOX = """
invocabulary { Val/1 Sum/2 }
outvocabulary { x/1 y/1 }
theory {
    ? a [Val(a)] : x(a).
    ! a [Val(a)] : ! b [Val(b) & ~(a = b)] : ~x(a) | ~x(b).
    ? a [Val(a)] : y(a).
    ! a [Val(a)] : ! b [Val(b) & ~(a = b)] : ~y(a) | ~y(b).
    ! a : ! b [Val(a) & Val(b) & ~Sum(a, b)] : ~x(a) | ~y(b).
}
"""


def structure(instance):
    n = instance["n"]
    return {"Val": range(n + 1),
            "Sum": [(a, b) for a in range(n + 1) for b in range(n + 1) if a + b == n]}
