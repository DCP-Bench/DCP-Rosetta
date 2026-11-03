// Two disjoint non-empty subsets S and T of the given set A with equal sums.
// Instance field A: the list of distinct integers. Output in_S[i] = 1 if A[i] is in S, in_T[i] = 1 if A[i] is in T.
// The number of elements is read from A.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray a = inst.getJSONArray("A");
        int n = a.length();

        // inS[i] and inT[i]: whether element i is in S, and whether it is in T
        BooleanVar[] inS = new BooleanVar[n];
        BooleanVar[] inT = new BooleanVar[n];
        for (int i = 0; i < n; i++) {
            inS[i] = new BooleanVar(store, "in_S_" + i);
            inT[i] = new BooleanVar(store, "in_T_" + i);
        }

        // S and T are disjoint: no element is in both
        for (int i = 0; i < n; i++) {
            store.impose(new LinearInt(new IntVar[]{inS[i], inT[i]}, new int[]{1, 1}, "<=", 1));
        }

        // S and T are non-empty: at least one element in each
        int[] unit = new int[n];
        for (int i = 0; i < n; i++) {
            unit[i] = 1;
        }
        store.impose(new LinearInt(inS, unit, ">=", 1));
        store.impose(new LinearInt(inT, unit, ">=", 1));

        // equal sums: the sum of the elements of S equals the sum of the elements of T
        // sum over S of A[i] minus sum over T of A[i] equals 0
        IntVar[] members = new IntVar[2 * n];
        int[] weights = new int[2 * n];
        for (int i = 0; i < n; i++) {
            members[i] = inS[i];
            weights[i] = a.getInt(i);
            members[n + i] = inT[i];
            weights[n + i] = -a.getInt(i);
        }
        store.impose(new LinearInt(members, weights, "==", 0));

        return new Model().put("in_S", inS).put("in_T", inT);
    }
}
