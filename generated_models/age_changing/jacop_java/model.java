// Age changing: the wife (m) applies the four operations +2, /8, -3, *7 once each, in some
// order, and gets the husband's age (h). The husband applies the same four operations in a
// different order and gets the wife's age. Find m and h.
// Outputs: "m" (the wife's age), "h" (the husband's age).
//
// Encoding: each sequence has four steps. Step j chooses an operation index s[j] in 0..3
// (0 = +2, 1 = -3, 2 = *7, 3 = /8), and the four operations are a permutation (Alldifferent).
// Each step computes all four results and picks one with Element. The division must be exact,
// so when the step is /8 the value must equal 8 times its quotient. The two sequences differ
// in at least one step.
// The problem has no instance data, so every bound is a constant. Ages are 0..1000 and the
// intermediate values are 0..7000 (7 times the largest age).
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.Element;
import org.jacop.constraints.Implies;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XeqY;
import org.jacop.constraints.XneqY;
import org.jacop.constraints.XmulCeqZ;
import org.jacop.constraints.XplusCeqZ;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import org.jacop.search.IndomainMin;
import dcp.jacop.Model;

public class Submission {
    static final int AGE_MAX = 1000;
    static final int VALUE_MAX = 7 * AGE_MAX;

    public static Model build(JSONObject inst, Store store) {
        IntVar m = new IntVar(store, "m", 0, AGE_MAX);   // wife's age
        IntVar h = new IntVar(store, "h", 0, AGE_MAX);   // husband's age

        // Operation choices for the two sequences, one per step.
        IntVar[] s1 = new IntVar[4];   // wife -> husband
        IntVar[] s2 = new IntVar[4];   // husband -> wife
        for (int j = 0; j < 4; j++) {
            s1[j] = new IntVar(store, "s1_" + j, 0, 3);
            s2[j] = new IntVar(store, "s2_" + j, 0, 3);
        }
        // Each operation is used exactly once in each sequence.
        store.impose(new Alldifferent(s1));
        store.impose(new Alldifferent(s2));

        // The first sequence takes the wife's age to the husband's age.
        IntVar end1 = chain(store, m, s1, "a");
        store.impose(new XeqY(end1, h));

        // The second sequence takes the husband's age to the wife's age.
        IntVar end2 = chain(store, h, s2, "b");
        store.impose(new XeqY(end2, m));

        // "A different order": at some step the two sequences choose different operations.
        IntVar[] differ = new IntVar[4];
        for (int j = 0; j < 4; j++) {
            differ[j] = new BooleanVar(store, "differ_" + j);
            store.impose(new Reified(new XneqY(s1[j], s2[j]), (BooleanVar) differ[j]));
        }
        store.impose(new LinearInt(differ, new int[]{1, 1, 1, 1}, ">=", 1));

        IntVar[] order = new IntVar[8];
        for (int j = 0; j < 4; j++) {
            order[j] = s1[j];
            order[4 + j] = s2[j];
        }
        return new Model().put("m", m).put("h", h).search(order, null, new IndomainMin<>());
    }

    // Applies one sequence of four operations, chosen by s[0..3], to start.
    // Returns the variable holding the result after the fourth step.
    static IntVar chain(Store store, IntVar start, IntVar[] s, String tag) {
        IntVar x = start;
        for (int j = 0; j < 4; j++) {
            // The four candidate results of this step.
            IntVar plus = new IntVar(store, tag + j + "_plus2", 0, VALUE_MAX);   // x + 2
            IntVar minus = new IntVar(store, tag + j + "_minus3", 0, VALUE_MAX);  // x - 3
            IntVar times = new IntVar(store, tag + j + "_times7", 0, VALUE_MAX);  // 7 * x
            IntVar quot = new IntVar(store, tag + j + "_div8", 0, VALUE_MAX);     // x / 8

            store.impose(new XplusCeqZ(x, 2, plus));
            store.impose(new XmulCeqZ(x, 7, times));

            // x - 3 is only defined when the step is -3: then minus + 3 = x.
            BooleanVar isMinus = new BooleanVar(store, tag + j + "_isMinus");
            store.impose(new Reified(new XeqC(s[j], 1), isMinus));
            store.impose(new Implies(isMinus, new XplusCeqZ(minus, 3, x)));

            // x / 8 must be exact when the step is /8: then 8 * quot = x.
            BooleanVar isDiv = new BooleanVar(store, tag + j + "_isDiv");
            store.impose(new Reified(new XeqC(s[j], 3), isDiv));
            store.impose(new Implies(isDiv,
                new LinearInt(new IntVar[]{quot, x}, new int[]{8, -1}, "==", 0)));

            // The result of this step is the candidate chosen by s[j] (0 = +2, 1 = -3, 2 = *7, 3 = /8).
            IntVar y = new IntVar(store, tag + j + "_out", 0, VALUE_MAX);
            store.impose(Element.choose(s[j], new IntVar[]{plus, minus, times, quot}, y, -1));
            x = y;
        }
        return x;
    }
}
