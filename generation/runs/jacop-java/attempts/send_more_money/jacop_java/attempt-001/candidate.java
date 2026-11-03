// SEND + MORE = MONEY: each letter is a distinct digit 0-9, and the first letters S and M are not zero.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XneqC;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    public static Model build(JSONObject instance, Store store) {
        IntVar s = new IntVar(store, "s", 0, 9);
        IntVar e = new IntVar(store, "e", 0, 9);
        IntVar n = new IntVar(store, "n", 0, 9);
        IntVar d = new IntVar(store, "d", 0, 9);
        IntVar m = new IntVar(store, "m", 0, 9);
        IntVar o = new IntVar(store, "o", 0, 9);
        IntVar r = new IntVar(store, "r", 0, 9);
        IntVar y = new IntVar(store, "y", 0, 9);
        IntVar[] letters = {s, e, n, d, m, o, r, y};

        // Each letter stands for a different digit.
        store.impose(new Alldifferent(letters));
        // The first letter of each word is not zero.
        store.impose(new XneqC(s, 0));
        store.impose(new XneqC(m, 0));

        // SEND + MORE = MONEY, moved to one side:
        // (1000 S + 100 E + 10 N + D) + (1000 M + 100 O + 10 R + E) - (10000 M + 1000 O + 100 N + 10 E + Y) = 0,
        // which collects to 1000 S + 91 E - 90 N + D - 9000 M - 900 O + 10 R - Y = 0.
        IntVar[] vars = {s, e, n, d, m, o, r, y};
        int[] weights = {1000, 91, -90, 1, -9000, -900, 10, -1};
        store.impose(new LinearInt(vars, weights, "==", 0));

        return new Model().put("s", s).put("e", e).put("n", n).put("d", d)
            .put("m", m).put("o", o).put("r", r).put("y", y)
            .search(letters, null, null);
    }
}
