# csplib_002_template_design, jacop_java, attempt-001

Not retained. The evaluator accepted it only by skipping json:2 (3 templates). Available instances: 2 (the catfood2 row equals the example data and gets no ID). Checked: 1 of 2, below the 80% rule.

- Example (2 templates): solved in about 1 s with layouts labelled first, IndomainMin.
- json:2 (3 templates, optimum 408 = ceil(3665 / 9)): no solution in 180 s under any tried search order (layouts first or production first, IndomainMin or IndomainMax, SmallestDomain). The runner reports `timeout` with zero solutions.
- Likely cause: the product `layout[t][v] * production[t]` gives weak bounds propagation, so the depth-first search cannot prune the layout and production combinations.
- Not added: a symmetry breaking on template order, and a forced full layout (every slot filled). Both are valid dominance arguments but the description does not ask for them, so they were left out.
