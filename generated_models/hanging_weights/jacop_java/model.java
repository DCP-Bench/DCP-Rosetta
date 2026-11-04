// Hanging weights: weights a..m hang from a system of bars; each weight is an integer in 1..13,
// and every bar balances (weights on either side of its pivot, times their distance, are equal).
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        // each weight is an integer between 1 and 13 (the instance carries no data)
        IntVar a = new IntVar(store, "a", 1, 13);
        IntVar b = new IntVar(store, "b", 1, 13);
        IntVar c = new IntVar(store, "c", 1, 13);
        IntVar d = new IntVar(store, "d", 1, 13);
        IntVar e = new IntVar(store, "e", 1, 13);
        IntVar f = new IntVar(store, "f", 1, 13);
        IntVar g = new IntVar(store, "g", 1, 13);
        IntVar h = new IntVar(store, "h", 1, 13);
        IntVar i = new IntVar(store, "i", 1, 13);
        IntVar j = new IntVar(store, "j", 1, 13);
        IntVar k = new IntVar(store, "k", 1, 13);
        IntVar l = new IntVar(store, "l", 1, 13);
        IntVar m = new IntVar(store, "m", 1, 13);

        // bar A-B (pivot under the bar's middle): A hangs 4 units left of the pivot, B 1 unit right
        store.impose(new LinearInt(new IntVar[]{a, b}, new int[]{4, -1}, "==", 0));    // 4*A = B
        // bar C-D (bottom right): C hangs 5 units left of the pivot, D 1 unit right
        store.impose(new LinearInt(new IntVar[]{c, d}, new int[]{5, -1}, "==", 0));    // 5*C = D
        // bar G over bar C-D: G hangs 3 units left, the whole bar C-D (C+D) 2 units right
        store.impose(new LinearInt(new IntVar[]{g, c, d}, new int[]{3, -2, -2}, "==", 0)); // 3*G = 2*(C+D)
        // bar E-F: E hangs 3 units left of the pivot, F 2 units right
        store.impose(new LinearInt(new IntVar[]{e, f}, new int[]{3, -2}, "==", 0));    // 3*E = 2*F
        // bar H-I (with bar E-F hanging 2 units right of the pivot): H 3 left, I 3 right
        // 3*H = 3*I + 2*(E+F)
        store.impose(new LinearInt(new IntVar[]{h, i, e, f}, new int[]{3, -3, -2, -2}, "==", 0));
        // bar L-M (with bar H-I-E-F hanging 1 unit left of the pivot): L 1 unit right, M 4 units right
        // (H+I+E+F) = L + 4*M
        store.impose(new LinearInt(new IntVar[]{h, i, e, f, l, m}, new int[]{1, 1, 1, 1, -1, -4}, "==", 0));
        // bar J-K (with bar A-B hanging 3 units left and bar G-C-D 2 units right of the pivot):
        // J 2 units left, K 1 unit right
        // 3*(A+B) + 2*J = K + 2*(G+C+D)
        store.impose(new LinearInt(new IntVar[]{a, b, j, k, g, c, d},
                new int[]{3, 3, 2, -1, -2, -2, -2}, "==", 0));
        // top bar: the left half (L, M, H, I, E, F) hangs 4 units left of the pivot, the right half
        // (J, K, A, B, G, C, D) 3 units right. 4*(left total) = 3*(right total)
        store.impose(new LinearInt(new IntVar[]{l, m, h, i, e, f, j, k, a, b, g, c, d},
                new int[]{4, 4, 4, 4, 4, 4, -3, -3, -3, -3, -3, -3, -3}, "==", 0));

        Model model = new Model()
                .put("a", a).put("b", b).put("c", c).put("d", d).put("e", e).put("f", f)
                .put("g", g).put("h", h).put("i", i).put("j", j).put("k", k).put("l", l).put("m", m);
        return model;
    }
}
