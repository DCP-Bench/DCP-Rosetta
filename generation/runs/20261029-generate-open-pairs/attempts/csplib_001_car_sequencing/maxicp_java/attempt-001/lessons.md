Blind model, after reading the lessons of 20261016-maxicp-java-models (only the example solved).
MaxiCP's driver fixes the search (firstFailBinary, smallest value first), so the search is set
through the model: one Boolean per (slot, type rank), registered slot by slot, each the negation
of a registered Boolean, gives a left-to-right fill that tries types in a chosen order. Measured
locally at 120 s on the 22 instances:
- an integer rank per slot (firstFail jumps between slots): most 200-car instances time out;
- one-hot left-to-right, types by option load: 17 of 22 (7, 13, 14, 17, 20 time out, also at 178 s);
- option-first decisions, the two most loaded options first, all-prefix bounds, suffix bounds,
  reverse fill, other load measures: 6 to 14 failures;
- one-hot, types by option load divided by sqrt(demand): 22 of 22 within 10 s. That is this
  attempt. The scaling is empirical and the model says so.
The Choco model of the same run reached 22 of 22 with a dynamic value order, which MaxiCP's
driver cannot express.
