import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.search.strategy.selectors.variables.InputOrder;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Car sequencing (CSPLib 001): put the cars to be produced in a row on the assembly line so
// that every option station sees at most at_most[o] cars needing option o in any
// per_slots[o] consecutive cars, and each car type appears exactly demand[t] times.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] atMost = inst.getIntArray("at_most");
    int[] perSlots = inst.getIntArray("per_slots");
    int[] demand = inst.getIntArray("demand");
    int[][] requires = inst.getIntMatrix("requires");
    int nTypes = demand.length;
    int nOptions = atMost.length;
    int nCars = 0;
    for (int d : demand) nCars += d;

    // sequence[i]: the car type in slot i of the line (types numbered from 0)
    IntVar[] sequence = m.intVarArray("sequence", nCars, 0, nTypes - 1);

    // each car type is produced exactly as often as it is demanded
    int[] types = new int[nTypes];
    IntVar[] occurrences = new IntVar[nTypes];
    for (int t = 0; t < nTypes; t++) {
      types[t] = t;
      occurrences[t] = m.intVar(demand[t]);
    }
    m.globalCardinality(sequence, types, occurrences, true).post();

    // uses[o][i] = 1 when the car in slot i needs option o (read from the requires table)
    BoolVar[][] uses = new BoolVar[nOptions][nCars];
    for (int o = 0; o < nOptions; o++) {
      int[] column = new int[nTypes];
      int total = 0;
      for (int t = 0; t < nTypes; t++) {
        column[t] = requires[t][o];
        total += requires[t][o] * demand[t];
      }
      for (int i = 0; i < nCars; i++) {
        uses[o][i] = m.boolVar("uses_" + o + "_" + i);
        m.element(uses[o][i], column, sequence[i]).post();
      }

      // the station for option o copes with at most at_most[o] cars in any per_slots[o] in a row
      int p = perSlots[o], k = atMost[o];
      for (int start = 0; start + p <= nCars; start++) {
        BoolVar[] window = new BoolVar[p];
        System.arraycopy(uses[o], start, window, 0, p);
        m.sum(window, "<=", k).post();
      }

      // implied: the number of cars needing option o is fixed by the demand, and the last
      // j windows of the line can hold at most j*at_most of them, so the slots before them
      // must hold the rest (the classic car-sequencing redundant constraint)
      m.sum(uses[o], "=", total).post();
      for (int j = 1; j * p < nCars; j++) {
        int prefix = nCars - j * p;
        int need = total - j * k;
        if (need <= 0) break;
        BoolVar[] head = new BoolVar[prefix];
        System.arraycopy(uses[o], 0, head, 0, prefix);
        m.sum(head, ">=", need).post();
      }
    }

    // Fill the line from its first slot. For the car type, take the one whose options are the
    // most loaded at this point: an option's load is the number of cars still needing it over the
    // capacity its station has left in the unfilled slots (at_most per per_slots of them).
    final int[] totalOf = new int[nOptions];
    for (int o = 0; o < nOptions; o++)
      for (int t = 0; t < nTypes; t++) totalOf[o] += requires[t][o] * demand[t];
    final IntVar[] line = sequence;
    m.getSolver().setSearch(Search.intVarSearch(new InputOrder<>(m), (IntVar v) -> {
      int[] left = totalOf.clone();
      int open = 0;
      for (IntVar s : line) {
        if (s.isInstantiated()) {
          for (int o = 0; o < nOptions; o++) left[o] -= requires[s.getValue()][o];
        } else open++;
      }
      double[] load = new double[nOptions];
      for (int o = 0; o < nOptions; o++) load[o] = left[o] / (open * (double) atMost[o] / perSlots[o] + 1e-9);
      int best = v.getLB();
      double bestScore = -1;
      for (int t = v.getLB(); t <= v.getUB(); t = v.nextValue(t)) {
        double score = 0;
        for (int o = 0; o < nOptions; o++) score += requires[t][o] * load[o];
        if (score > bestScore) { bestScore = score; best = t; }
      }
      return best;
    }, sequence));

    out.put("sequence", sequence);
  }
}
