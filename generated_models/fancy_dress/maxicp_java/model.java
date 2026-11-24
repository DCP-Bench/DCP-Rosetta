import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Fancy dress: Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and
// pays the $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total
// cost. He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // The instance has no fields: every number below is from the problem statement.
    CPBoolVar t = m.boolVar();  // he wears a green tie
    CPBoolVar h = m.boolVar();  // he wears a green hat
    CPBoolVar r = m.boolVar();  // he wears a green shirt
    CPBoolVar s = m.boolVar();  // he wears green socks
    CPBoolVar n = m.boolVar();  // he pays the entrance fee

    // Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee, so each
    // rule holds or he pays. Each rule "if A then B" is the clause "not A or B".
    // Rule 1: if someone wears a green tie he has to wear a green shirt.
    m.cp().post(or(new CPBoolVar[]{not(t), r, n}));
    // Rule 2: a guest who wears green socks or a green shirt must also wear a green tie or
    // a green hat.
    CPBoolVar socksOrShirt = isOr(s, r);
    m.cp().post(or(new CPBoolVar[]{not(socksOrShirt), t, h, n}));
    // Rule 3: a guest wearing a green shirt or a green hat or who does not wear green socks
    // must wear a green tie.
    CPBoolVar needsTie = isOr(r, h, not(s));
    m.cp().post(or(new CPBoolVar[]{not(needsTie), t, n}));

    // Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
    m.minimize(sum(mul(t, 10), mul(h, 2), mul(s, 12), mul(n, 11)));

    out.put("t", t);
    out.put("h", h);
    out.put("r", r);
    out.put("s", s);
    out.put("n", n);
  }
}
