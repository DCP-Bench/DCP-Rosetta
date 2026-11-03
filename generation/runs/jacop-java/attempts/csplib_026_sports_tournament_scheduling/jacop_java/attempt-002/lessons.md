# Lessons: csplib_026 on jacop_java, attempt 2

- hints.md (coordinator's scratch hints) was used.
- Accepted on both instances (n=8 in 1 s, n=6 in 0.1 s), two valid solutions each.
- Attempt 1 was rejected because of Alldistinct (wrong second solution under the runner's enumeration)
  and a slow IfThen channelling. Fix: Alldifferent everywhere, and per week an opponent array tied to the
  slots with Element.choose(home, opp[w], away, 0) in both directions (teams are 1-based list indices, offset 0).
- Count(inPeriod, times, t) with a fresh counter variable 0..2 for the period rule.
- Symmetry rules allowed because nothing in the reference depends on orientation or labels: home < away,
  week 1 = (1,2),(3,4),...
- Search: slots week by week in input order, IndomainMin.
