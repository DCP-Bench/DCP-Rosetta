import java.util.Arrays;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.SettingsBuilder;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Coins grid: place coins on an n x n board, at most one per cell, with exactly c coins in
// every row and every column, so that the sum over the coins of the squared horizontal
// distance (i - j)^2 of their cell from the main diagonal is as small as possible.
public class Submission {
  // Lazy clause generation: the model only uses Boolean sums and a weighted sum, both on the
  // skill's list of constraints checked under LCG.
  public static SettingsBuilder settings() {
    return SettingsBuilder.init().setLCG(true);
  }

  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int c = inst.getInt("c");

    // x[i][j] = 1 when a coin lies on cell (i, j); a cell holds at most one coin
    BoolVar[][] x = m.boolVarMatrix("x", n, n);

    // in each row exactly c coins
    for (int i = 0; i < n; i++) m.sum(x[i], "=", c).post();
    // in each column exactly c coins
    for (int j = 0; j < n; j++) {
      BoolVar[] col = new BoolVar[n];
      for (int i = 0; i < n; i++) col[i] = x[i][j];
      m.sum(col, "=", c).post();
    }

    // the cost of a row is the squared distance of its coins from the diagonal; it is at least
    // the sum of the c smallest squared distances available in that row (a bound derived from
    // the row constraint, which helps the optimality proof)
    IntVar[] rowCost = new IntVar[n];
    int lowerBound = 0, upper = 0;
    for (int i = 0; i < n; i++) {
      int[] w = new int[n];
      for (int j = 0; j < n; j++) w[j] = (i - j) * (i - j);
      int[] sorted = w.clone();
      Arrays.sort(sorted);
      int lo = 0, hi = 0;
      for (int k = 0; k < c; k++) {
        lo += sorted[k];
        hi += sorted[n - 1 - k];
      }
      lowerBound += lo;
      upper += hi;
      rowCost[i] = m.intVar("rowCost_" + i, lo, hi, true);
      m.scalar(x[i], w, "=", rowCost[i]).post();
    }

    // z: the sum of the squared horizontal distances from the main diagonal, to be minimised
    IntVar z = m.intVar("z", lowerBound, upper, true);
    m.sum(rowCost, "=", z).post();
    m.setObjective(Model.MINIMIZE, z);

    // no search is set: Choco's default black-box search with LCG proved the optimum fastest

    out.put("x", x);
    out.put("z", z);
  }
}
