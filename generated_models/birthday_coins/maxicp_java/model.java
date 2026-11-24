import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Birthday coins: Tommy was given 15 coins, each a half-crown (30 pence), a shilling (12 pence)
// or a sixpence (6 pence), though not necessarily coins of all three kinds. Together they are
// worth £1 5s 6d. How many half-crowns could he have been given?
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // The instance has no fields: every number below is from the problem statement.
    // How many coins of each kind he was given: a kind may be absent (0), and no kind can
    // number more than the 15 coins.
    CPIntVar halfCrowns = m.intVar(0, 15);
    CPIntVar shillings = m.intVar(0, 15);
    CPIntVar sixpences = m.intVar(0, 15);

    // He was given 15 coins.
    m.cp().post(eq(sum(halfCrowns, shillings, sixpences), 15));

    // They add up to £1 5s 6d = 240 + 5 * 12 + 6 = 306 pence; a half-crown is 30 pence, a
    // shilling 12 and a sixpence 6.
    m.cp().post(eq(sum(mul(halfCrowns, 30), mul(shillings, 12), mul(sixpences, 6)), 306));

    out.put("half_crowns", halfCrowns);
  }
}
