import re, subprocess
from pysat.solvers import Solver
nodes, colours, edges = [0, 1, 2, 3], ["red", "green", "blue"], [(0, 1), (1, 2), (2, 0), (2, 3)]
fox = """invocabulary { Node/1 Colour/1 Edge/2 }
outvocabulary { colour/2 }
theory {
    ! n [Node(n)] : ? c [Colour(c)] : colour(n, c).
    ! n [Node(n)] : ! c [Colour(c)] : ! d [Colour(d) & c ~= d] : ~colour(n, c) | ~colour(n, d).
    ! a : ! b [Edge(a, b)] : ! c [Colour(c)] : ~colour(a, c) | ~colour(b, c).
}
structure {
    domain = { %s }
    Node = { %s }
    Colour = { %s }
    Edge = { %s }
}
""" % (" ; ".join(map(str, nodes + colours)), " ; ".join(map(str, nodes)), " ; ".join(colours),
       " ; ".join(f"({a},{b})" for a, b in edges))
open("colouring.fox", "w").write(fox)
subprocess.run(["groundfox", "-i", "colouring.fox", "-o", "colouring.cnf", "-t", "colouring.sym", "--no-proof"],
               check=True, capture_output=True)
clauses = [[int(x) for x in line.split()[:-1]] for line in open("colouring.cnf") if line[0] not in "cp"]
atoms = {int(v): a for _, v, a in (line.split(None, 2) for line in open("colouring.sym"))}
with Solver(name="glucose42", bootstrap_with=clauses) as solver:
    if solver.solve():
        print(sorted(atoms[v].strip() for v in solver.get_model() if v > 0 and v in atoms))
    else:
        print("unsatisfiable")
