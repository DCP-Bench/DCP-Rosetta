import java.util.Arrays;
import java.util.Comparator;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
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
    int nTypes = demand.length, nOptions = atMost.length;
    int nCars = 0;
    for (int d : demand) nCars += d;
    CPSolver cp = m.cp();

    // A value order for the search: the car types sorted from hardest to easiest. An option's load
    // is the number of cars needing it over the most its station can take on the whole line; a
    // type's difficulty is the load of the options it needs, divided by the square root of its
    // demand, so that rare demanding types come before common ones. (The scaling was chosen by
    // trying orders on the instances' sizes; plain load left five 200-car instances unsolved.)
    // sequence[i], the type in slot i numbered from 0, is read through this order.
    double[] load = new double[nOptions];
    int[] total = new int[nOptions];
    for (int o = 0; o < nOptions; o++) {
      for (int t = 0; t < nTypes; t++) total[o] += requires[t][o] * demand[t];
      load[o] = total[o] / (nCars * (double) atMost[o] / perSlots[o]);
    }
    double[] difficulty = new double[nTypes];
    Integer[] order = new Integer[nTypes];
    for (int t = 0; t < nTypes; t++) {
      order[t] = t;
      for (int o = 0; o < nOptions; o++) difficulty[t] += requires[t][o] * load[o];
    }
    Arrays.sort(order, Comparator.comparingDouble((Integer t) -> -difficulty[t] / Math.sqrt(demand[t]))
        .thenComparingInt(t -> t));
    int[] typeAt = new int[nTypes];
    for (int k = 0; k < nTypes; k++) typeAt[k] = order[k];

    // pick[k]: slot i holds the type of rank k. These are the decisions, registered slot by slot
    // and rank by rank; all are Booleans, so firstFailBinary takes them in that order: it fills
    // the line from its first slot, trying the hardest type first. Each pick is the negation of a
    // registered Boolean, which is branched 0 first, so "take this type" is tried first.
    CPIntVar[] rank = new CPIntVar[nCars];
    CPIntVar[] sequence = new CPIntVar[nCars];
    for (int i = 0; i < nCars; i++) {
      rank[i] = makeIntVar(cp, 0, nTypes - 1);
      CPBoolVar[] pick = new CPBoolVar[nTypes];
      for (int k = 0; k < nTypes; k++) {
        pick[k] = not(m.boolVar());
        cp.post(eq(pick[k], isEq(rank[i], k)));
      }
      cp.post(sum(pick, 1));
      sequence[i] = element(typeAt, rank[i]);
    }

    // each car type is produced exactly as often as it is demanded
    for (int t = 0; t < nTypes; t++) {
      CPBoolVar[] isType = new CPBoolVar[nCars];
      for (int i = 0; i < nCars; i++) isType[i] = isEq(sequence[i], t);
      cp.post(sum(isType, demand[t]));
    }

    for (int o = 0; o < nOptions; o++) {
      // uses[i] = 1 when the car in slot i needs option o
      int[] column = new int[nTypes];
      for (int t = 0; t < nTypes; t++) column[t] = requires[t][o];
      CPIntVar[] uses = new CPIntVar[nCars];
      for (int i = 0; i < nCars; i++) uses[i] = element(column, sequence[i]);

      // the station for option o copes with at most at_most[o] cars in any per_slots[o] in a row
      int p = perSlots[o], k = atMost[o];
      for (int s = 0; s + p <= nCars; s++) cp.post(le(sum(Arrays.copyOfRange(uses, s, s + p)), k));

      // implied: the cars needing option o are fixed in number by the demand, and the last j
      // windows of the line hold at most j*at_most of them, so the slots before hold the rest
      cp.post(sum(uses, total[o]));
      for (int j = 1; j * p < nCars; j++) {
        int need = total[o] - j * k;
        if (need <= 0) break;
        cp.post(ge(sum(Arrays.copyOfRange(uses, 0, nCars - j * p)), need));
      }
    }

    out.put("sequence", sequence);
  }
}
