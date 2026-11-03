# csplib_056_sonet: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_056_sonet.py csplib_056_sonet.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer
from pysat.pb import EncType as PBEncType, PBEnc


def create_model(instance):
    """Install nodes on rings, with each install using an add-drop multiplexer (ADM):
    nodes with traffic demand between them must share a ring, a ring hosts a limited
    number of nodes, and the total number of ADMs is as small as possible."""
    n_rings = instance["r"]                # the number of rings
    n_nodes = instance["n"]                # the number of nodes
    demand = instance["demand"]            # demand[i][j] > 0: nodes i and j communicate
    capacity = instance["capacity_nodes"]  # capacity[k]: the most nodes ring k can host

    pool = IDPool()
    formula = WCNF()

    # ring_config[k][i] is true when node i is installed on ring k, which takes one ADM.
    ring_config = [[pool.id(("ring_config", k, i)) for i in range(n_nodes)]
                   for k in range(n_rings)]

    # Nodes with traffic between them share a ring.
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if demand[i][j] > 0:
                # on_both[k] can be true only when nodes i and j are both on ring k.
                on_both = []
                for k in range(n_rings):
                    both = pool.id(("on_both", k, i, j))
                    formula.append([-both, ring_config[k][i]])
                    formula.append([-both, ring_config[k][j]])
                    on_both.append(both)
                formula.append(on_both)

    # Each ring holds no more nodes than its capacity.
    for k in range(n_rings):
        formula.extend(CardEnc.atmost(lits=ring_config[k], bound=capacity[k],
                                      vpool=pool, encoding=EncType.seqcounter).clauses)

    # The nodes each ring can hold: its capacity, or all n nodes if that is less.
    per_ring = [min(max(c, 0), n_nodes) for c in capacity]
    # The most ADMs any solution can use, and at least one.
    max_adms = max(sum(per_ring), 1)

    # total_adms is the number of ADMs used, from 0 to max_adms.
    total_adms = Integer("total_adms", 0, max_adms, encoding="coupled", vpool=pool)
    formula.extend(total_adms.domain_clauses())
    # reached[m - 1] is true when total_adms is at least m.
    reached = [total_adms.ge(m) for m in range(1, max_adms + 1)]

    # Every node installed on a ring, as one flat list.
    installs = [lit for row in ring_config for lit in row]
    # The number of ADMs equals the number of installations.
    formula.extend(PBEnc.equals(lits=installs + reached,
                                weights=[1] * len(installs) + [-1] * max_adms,
                                bound=0, vpool=pool,
                                encoding=PBEncType.bdd).clauses)

    # Each installation costs one ADM, and the total is minimised.
    for lit in installs:
        formula.append([-lit], weight=1)

    return formula, {"ring_config": ring_config, "total_adms": total_adms}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        # an Integer decodes its value from the model, a literal is true when it is in the model
        value = np.vectorize(lambda v: v.decode(model) if isinstance(v, Integer) else v in model)
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
