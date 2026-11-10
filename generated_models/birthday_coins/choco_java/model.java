import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Birthday coins: Tommy was given 15 coins, each a half-crown (30 pence), a shilling (12 pence)
// or a sixpence (6 pence), though not necessarily coins of all three kinds. Together they are
// worth £1 5s 6d. How many half-crowns could he have been given?
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // The instance has no fields: every number below is from the problem statement.
    // How many coins of each kind he was given: a kind may be absent (0), and no kind can
    // number more than the 15 coins.
    IntVar halfCrowns = m.intVar("half_crowns", 0, 15);
    IntVar shillings = m.intVar("shillings", 0, 15);
    IntVar sixpences = m.intVar("sixpences", 0, 15);
    IntVar[] coins = {halfCrowns, shillings, sixpences};

    // He was given 15 coins.
    m.sum(coins, "=", 15).post();

    // They add up to £1 5s 6d = 240 + 5 * 12 + 6 = 306 pence; a half-crown is 30 pence, a
    // shilling 12 and a sixpence 6.
    m.scalar(coins, new int[]{30, 12, 6}, "=", 306).post();

    out.put("half_crowns", halfCrowns);
  }
}
