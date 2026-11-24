import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Fancy dress: Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and
// pays the $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total
// cost. He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // The instance has no fields: every number below is from the problem statement.
    BoolVar t = m.boolVar("t");  // he wears a green tie
    BoolVar h = m.boolVar("h");  // he wears a green hat
    BoolVar r = m.boolVar("r");  // he wears a green shirt
    BoolVar s = m.boolVar("s");  // he wears green socks
    BoolVar n = m.boolVar("n");  // he pays the entrance fee

    // Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee, so each
    // rule holds or he pays.
    // Rule 1: if someone wears a green tie he has to wear a green shirt.
    t.imp(r).or(n).post();
    // Rule 2: a guest who wears green socks or a green shirt must also wear a green tie or
    // a green hat.
    s.or(r).imp(t.or(h)).or(n).post();
    // Rule 3: a guest wearing a green shirt or a green hat or who does not wear green socks
    // must wear a green tie.
    r.or(h, s.not()).imp(t).or(n).post();

    // Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
    IntVar cost = m.intVar("cost", 0, 10 + 2 + 12 + 11);
    m.scalar(new IntVar[]{t, h, s, n}, new int[]{10, 2, 12, 11}, "=", cost).post();
    m.setObjective(Model.MINIMIZE, cost);

    out.put("t", t);
    out.put("h", h);
    out.put("r", r);
    out.put("s", s);
    out.put("n", n);
  }
}
