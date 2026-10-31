Blind model. gcc on the line, element per slot and option, sliding-window sums, the option totals
and the classic prefix lower bounds (the last j windows hold at most j*at_most cars with the
option). The search decided everything, measured with local container runs on json:1..21:
- LCG with input order, LCG with Choco's default search, no LCG with input order, and dom/wdeg
  with Luby restarts all timed out on json:1 or found only one solution in 120 s.
- A static value order (hardest car type first, by option load) solved 16 of 21; adding restarts
  or last-conflict changed which instances failed, not how many.
- A dynamic value order, filling slots left to right and choosing the type whose options are the
  most loaded given the cars still to place and the slots left, found two solutions on every
  instance in about 5 s (this attempt: 22 of 22 accepted).
