# Lessons

- Operation choice per step: s[j] in 0..3 with Alldifferent over the four steps; Element.choose(s[j], {plus, minus, times, quot}, y, -1) picks the result. Element.choose must be imposed with store.impose.
- Conditional parts of an op go through Reified(XeqC(s,k), b) plus Implies(b, c). Unconditional constraints for an unused op (e.g. minus + 3 = x) would wrongly force x >= 3 on every step.
