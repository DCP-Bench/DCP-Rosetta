// Langford's problem (CSPLib 024): arrange the 2k numbers 1,1,2,2,...,k,k in one
// sequence so that the two copies of each number v have exactly v numbers between
// them, i.e. they sit at positions p and p + v + 1.
//
// Model: for each number v, a variable first[v] gives the position of its first copy
// (0-based), and second[v] = first[v] + v + 1 the position of its second copy. All
// 2k positions are distinct, so every position holds exactly one copy. The output
// sequence sol gives the number at each position, linked to the copies by Element.

import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.Element;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Instance data: k, the largest number; the sequence has 2k entries.
        int k = inst.getInt("k");
        int len = 2 * k;

        // sol[p] = the number at position p, from 1 to k (the declared output).
        IntVar[] sol = new IntVar[len];
        for (int p = 0; p < len; p++) {
            sol[p] = new IntVar(store, "sol_" + p, 1, k);
        }

        // first[v-1] and second[v-1]: positions of the two copies of number v.
        // The second copy is v + 1 positions after the first one.
        IntVar[] first = new IntVar[k];
        IntVar[] second = new IntVar[k];
        IntVar[] allPositions = new IntVar[len];
        for (int v = 1; v <= k; v++) {
            int gap = v + 1;
            first[v - 1] = new IntVar(store, "first_" + v, 0, len - 1 - gap);
            second[v - 1] = new IntVar(store, "second_" + v, gap, len - 1);
            // second = first + gap
            IntVar[] gapEq = {second[v - 1], first[v - 1]};
            store.impose(new LinearInt(gapEq, new int[]{1, -1}, "==", gap));
            allPositions[2 * (v - 1)] = first[v - 1];
            allPositions[2 * (v - 1) + 1] = second[v - 1];
        }

        // All 2k positions are distinct: every position holds exactly one copy.
        store.impose(new Alldifferent(allPositions));

        // The copies of v are at their positions: sol at those positions is v.
        for (int v = 1; v <= k; v++) {
            IntVar value = new IntVar(store, v, v);
            store.impose(Element.choose(first[v - 1], sol, value, -1));
            store.impose(Element.choose(second[v - 1], sol, value, -1));
        }

        // Labels the positions of the first copies; the rest follows from them.
        return new Model()
                .put("sol", sol)
                .search(first, null, null);
    }
}
