# session5_grocery, jacop_java, attempt-001 (not retained)

- Literal brief: prices positive, sum = total_price, product = total_price. For the example
  (711 cents, 4 items) no integer solution exists: the only 4-factor set with product 711 is
  (1,1,1,711), sum 714. The attempt is unsat on the example (`no_solution`).
- The reference (read after the failure, to diagnose) uses product == total_price * 100**(num_items-1),
  i.e. the product is scaled to cents. The brief and description do not say so, so the spec is
  incomplete. Not modelled: copying a scaling from the reference is not in the contract.
- Recorded as a reference blocker for every integration in generation/blockers.json.
