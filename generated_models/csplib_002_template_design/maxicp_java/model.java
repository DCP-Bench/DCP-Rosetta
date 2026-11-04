import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Template design (CSPLib 002): fill each of n_templates printing templates with exactly n_slots
// copies of the design variations, and choose how many sheets to print from each template, so
// that every variation is printed at least as often as demanded; minimise the sheets printed.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int nT = inst.getInt("n_templates"), nV = inst.getInt("n_var"), slots = inst.getInt("n_slots");
    int[] demand = inst.getIntArray("demand");
    CPSolver cp = m.cp();
    int totalDemand = 0, maxDemand = 0;
    for (int d : demand) {
      totalDemand += d;
      maxDemand = Math.max(maxDemand, d);
    }
    // Bounds on the sheets. Every sheet prints n_slots items, so at least
    // ceil(total demand / n_slots) sheets are needed. An optimal plan never prints more than the
    // largest demand from one template: every variation on it gets at least one copy per sheet, so
    // cutting that template's sheets to the largest demand keeps every demand met and costs less.
    int lowerBound = (totalDemand + slots - 1) / slots;
    int upperBound = nT * maxDemand;

    // production[t]: the sheets printed from template t
    CPIntVar[] production = new CPIntVar[nT];
    for (int t = 0; t < nT; t++) production[t] = makeIntVar(cp, 0, maxDemand);
    CPIntVar total = sum(production);

    // Search guide on the objective: reach[k] says "at most lowerBound + k sheets". These
    // Booleans are registered first and are the negation of registered Booleans, so the search
    // first looks for a plan with lowerBound sheets, then lowerBound + 1, and so on.
    int span = upperBound - lowerBound;
    for (int k = 0; k < span; k++) cp.post(eq(not(m.boolVar()), isLe(total, lowerBound + k)));

    // layout[t][v]: copies of variation v on template t; a template has exactly n_slots copies
    CPIntVar[][] layout = new CPIntVar[nT][];
    for (int t = 0; t < nT; t++) {
      layout[t] = m.intVarArray(nV, 0, slots);
      cp.post(sum(layout[t], slots));
    }

    // every variation is printed at least as often as demanded
    CPIntVar[] printed = new CPIntVar[nV];
    for (int v = 0; v < nV; v++) {
      CPIntVar[] parts = new CPIntVar[nT];
      for (int t = 0; t < nT; t++) parts[t] = mul(production[t], layout[t][v]);
      printed[v] = sum(parts);
      cp.post(ge(printed[v], demand[v]));
    }
    // implied: all items printed are n_slots per sheet
    cp.post(eq(sum(printed), mul(total, slots)));
    cp.post(ge(total, lowerBound));

    // minimise the sheets printed
    m.minimize(total);
    out.put("production", production);
    out.put("layout", layout);
  }
}
