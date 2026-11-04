# csplib_002_template_design: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python csplib_002_template_design.py csplib_002_template_design.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """Template design: a printer makes several variations of a carton on mother
    sheets. Each template has n_slots slots, and each slot holds one variation.
    Choose what each template holds and how many sheets to print from it, so that
    every variation reaches its demand with as few sheets as possible."""
    n_templates = instance["n_templates"]  # number of different templates
    n_var = instance["n_var"]              # number of variations
    n_slots = instance["n_slots"]          # number of slots on a template
    demand = instance["demand"]            # demand[v]: copies wanted of variation v

    # the most sheets printed from one template
    max_sheets = max(demand)
    n_sheet_bits = max_sheets.bit_length()

    # the most copies of one variation on one template: at most n_var, and at most n_slots
    max_copies = min(n_var, n_slots)
    n_copy_bits = max_copies.bit_length()

    # sheet_bit[t][j] is bit j of the number of sheets printed from template t
    sheet_bit = [[Bool(f"sheets_{t}_bit_{j}") for j in range(n_sheet_bits)]
                 for t in range(n_templates)]
    # production[t] is the number of sheets printed from template t
    production = [sum((2 ** j) * sheet_bit[t][j] for j in range(n_sheet_bits))
                  for t in range(n_templates)]

    # copy_bit[t][v][i] is bit i of the number of slots on template t that hold variation v
    copy_bit = [[[Bool(f"copies_{t}_{v}_bit_{i}") for i in range(n_copy_bits)]
                 for v in range(n_var)]
                for t in range(n_templates)]
    # layout[t][v] is the number of slots on template t that hold variation v
    layout = [[sum((2 ** i) * copy_bit[t][v][i] for i in range(n_copy_bits))
               for v in range(n_var)]
              for t in range(n_templates)]

    constraints = []

    # Every slot of every template holds a variation.
    for t in range(n_templates):
        constraints.append(sum(layout[t]) == n_slots)

    # Each variation takes at most max_copies slots on each template.
    for t in range(n_templates):
        for v in range(n_var):
            constraints.append(layout[t][v] <= max_copies)

    # A template is never printed more often than the largest demand: beyond that,
    # every variation it carries is already covered.
    for t in range(n_templates):
        constraints.append(production[t] <= max_sheets)

    # Each variation's demand is met: copies per sheet, times sheets, summed over the
    # templates. printed_bit is a product bit: set only when copy bit i of variation v
    # on template t and sheet bit j of template t are both set. Only that direction is
    # needed, since the demand constraint gains from set product bits.
    for v in range(n_var):
        printed_terms = []
        for t in range(n_templates):
            for i in range(n_copy_bits):
                for j in range(n_sheet_bits):
                    printed_bit = Bool(f"printed_{t}_{v}_{i}_{j}")
                    constraints.append(If(printed_bit, copy_bit[t][v][i] & sheet_bit[t][j]))
                    printed_terms.append((2 ** (i + j)) * printed_bit)
        constraints.append(sum(printed_terms) >= demand[v])

    # Redundant: every sheet carries n_slots copies, so the sheets printed must
    # cover the total demand.
    constraints.append(sum(production) * n_slots >= sum(demand))

    # Templates are interchangeable, so they are listed by sheets printed, largest first.
    for t in range(n_templates - 1):
        constraints.append(production[t] >= production[t + 1])

    # copy_vector[v] reads the copies of variation v on all templates as one number,
    # template 0 most significant, with digits up to max_copies.
    radix = max_copies + 1
    copy_vector = [sum(radix ** (n_templates - 1 - t) * layout[t][v] for t in range(n_templates))
                   for v in range(n_var)]
    # Variations with equal demand are interchangeable, so their copy vectors are ordered.
    for v in range(n_var - 1):
        if demand[v] == demand[v + 1]:
            constraints.append(copy_vector[v] >= copy_vector[v + 1])

    # Minimise the total number of sheets printed.
    total_sheets = sum(production)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_sheets, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"layout": layout, "production": production}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
