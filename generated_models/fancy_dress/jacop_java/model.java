import org.jacop.constraints.IfThen;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Or;
import org.jacop.constraints.PrimitiveConstraint;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

// Fancy dress: Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and
// pays the $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total
// cost. He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12.
public class Submission {
    // "v holds": the 0/1 variable v is 1
    private static PrimitiveConstraint yes(IntVar v) {
        return new XeqC(v, 1);
    }

    // "v does not hold": the 0/1 variable v is 0
    private static PrimitiveConstraint no(IntVar v) {
        return new XeqC(v, 0);
    }

    // at least one of the conditions holds
    private static PrimitiveConstraint anyOf(PrimitiveConstraint... cs) {
        return new Or(cs);
    }

    public static Model build(JSONObject inst, Store store) {
        // The instance has no fields: every number below is from the problem statement.
        BooleanVar t = new BooleanVar(store, "t");  // he wears a green tie
        BooleanVar h = new BooleanVar(store, "h");  // he wears a green hat
        BooleanVar r = new BooleanVar(store, "r");  // he wears a green shirt
        BooleanVar s = new BooleanVar(store, "s");  // he wears green socks
        BooleanVar n = new BooleanVar(store, "n");  // he pays the entrance fee

        // Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee, so
        // each rule holds or he pays.
        // Rule 1: if someone wears a green tie he has to wear a green shirt.
        store.impose(anyOf(new IfThen(yes(t), yes(r)), yes(n)));
        // Rule 2: a guest who wears green socks or a green shirt must also wear a green tie
        // or a green hat.
        store.impose(anyOf(new IfThen(anyOf(yes(s), yes(r)), anyOf(yes(t), yes(h))), yes(n)));
        // Rule 3: a guest wearing a green shirt or a green hat or who does not wear green
        // socks must wear a green tie.
        store.impose(anyOf(new IfThen(anyOf(yes(r), yes(h), no(s)), yes(t)), yes(n)));

        // Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he
        // owns).
        IntVar cost = new IntVar(store, "cost", 0, 10 + 2 + 12 + 11);
        store.impose(new LinearInt(new IntVar[]{t, h, s, n, cost}, new int[]{10, 2, 12, 11, -1}, "==", 0));

        return new Model().put("t", t).put("h", h).put("r", r).put("s", s).put("n", n)
                .minimize(cost)
                .search(new IntVar[]{t, h, r, s, n}, null, null);
    }
}
