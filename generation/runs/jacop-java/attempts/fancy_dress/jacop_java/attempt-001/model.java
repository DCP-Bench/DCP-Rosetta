// Fancy dress party: Mr Greenguest chooses which green items to wear so that the total cost
// is minimal. t = green tie, h = green hat, r = green shirt (owned, so free), s = green socks,
// n = entrance fee of 11 (paid when a dress rule is broken). Each choice costs
// 10 (tie), 2 (hat), 12 (socks), and the fee 11. The rules are not hard constraints: breaking
// one means the fee is paid. Each Boolean connective (and, or, implication) is written as
// linear inequalities over 0/1 variables with LinearInt.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        BooleanVar t = new BooleanVar(store, "tie");
        BooleanVar h = new BooleanVar(store, "hat");
        BooleanVar r = new BooleanVar(store, "shirt");
        BooleanVar s = new BooleanVar(store, "socks");
        BooleanVar n = new BooleanVar(store, "fee");

        // q = tie or hat (rule 2 reads: socks and shirt need a green tie or a green hat)
        BooleanVar q = new BooleanVar(store, "tieOrHat");
        lin(store, new IntVar[]{q, t}, new int[]{1, -1}, ">=", 0);
        lin(store, new IntVar[]{q, h}, new int[]{1, -1}, ">=", 0);
        lin(store, new IntVar[]{q, t, h}, new int[]{1, -1, -1}, "<=", 0);

        // p = shirt or hat or not socks (rule 3 premise)
        BooleanVar p = new BooleanVar(store, "shirtOrHatOrNoSocks");
        lin(store, new IntVar[]{p, r}, new int[]{1, -1}, ">=", 0);
        lin(store, new IntVar[]{p, h}, new int[]{1, -1}, ">=", 0);
        lin(store, new IntVar[]{p, s}, new int[]{1, 1}, ">=", 1);
        lin(store, new IntVar[]{p, r, h, s}, new int[]{1, -1, -1, 1}, "<=", 1);

        // v1 = rule 1 broken: green tie without green shirt
        BooleanVar v1 = new BooleanVar(store, "rule1Broken");
        lin(store, new IntVar[]{v1, t}, new int[]{1, -1}, "<=", 0);
        lin(store, new IntVar[]{v1, r}, new int[]{1, 1}, "<=", 1);
        lin(store, new IntVar[]{v1, t, r}, new int[]{1, -1, 1}, ">=", 0);

        // v2 = rule 2 broken: green socks and green shirt without green tie or green hat
        BooleanVar v2 = new BooleanVar(store, "rule2Broken");
        lin(store, new IntVar[]{v2, s}, new int[]{1, -1}, "<=", 0);
        lin(store, new IntVar[]{v2, r}, new int[]{1, -1}, "<=", 0);
        lin(store, new IntVar[]{v2, q}, new int[]{1, 1}, "<=", 1);
        lin(store, new IntVar[]{v2, s, r, q}, new int[]{1, -1, -1, 1}, ">=", -1);

        // v3 = rule 3 broken: shirt, hat or no socks, but no green tie
        BooleanVar v3 = new BooleanVar(store, "rule3Broken");
        lin(store, new IntVar[]{v3, p}, new int[]{1, -1}, "<=", 0);
        lin(store, new IntVar[]{v3, t}, new int[]{1, 1}, "<=", 1);
        lin(store, new IntVar[]{v3, p, t}, new int[]{1, -1, 1}, ">=", 0);

        // The fee is paid exactly when some rule is broken: n = v1 or v2 or v3.
        lin(store, new IntVar[]{n, v1}, new int[]{1, -1}, ">=", 0);
        lin(store, new IntVar[]{n, v2}, new int[]{1, -1}, ">=", 0);
        lin(store, new IntVar[]{n, v3}, new int[]{1, -1}, ">=", 0);
        lin(store, new IntVar[]{n, v1, v2, v3}, new int[]{1, -1, -1, -1}, "<=", 0);

        // Total cost: 10 tie + 2 hat + 12 socks + 11 fee, to be minimised.
        IntVar cost = new IntVar(store, "cost", 0, 35);
        lin(store, new IntVar[]{t, h, s, n, cost}, new int[]{10, 2, 12, 11, -1}, "==", 0);

        return new Model()
            .put("t", t).put("h", h).put("r", r).put("s", s).put("n", n)
            .minimize(cost)
            .search(new IntVar[]{t, h, r, s, n}, null, null);
    }

    private static void lin(Store store, IntVar[] x, int[] w, String op, int c) {
        store.impose(new LinearInt(x, w, op, c));
    }
}
