// Joe's account number: a permutation x of the digits 0..n-1 such that, for each
// tried set (also a permutation of 0..n-1), exactly k digits are in the same
// position as in x, where k is num_correct_digits.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // The sets and the number k of correct digits come from the instance.
        JSONArray sets = inst.getJSONArray("sets");
        int k = inst.getInt("num_correct_digits");
        int numSets = sets.length();
        // Each set has n digits, so n is the length of a set.
        int n = sets.getJSONArray(0).length();

        // x[i] is the digit in position i of the account number, 0..n-1.
        IntVar[] x = new IntVar[n];
        for (int i = 0; i < n; i++) {
            x[i] = new IntVar(store, "x" + i, 0, n - 1);
        }
        // The account number has every digit exactly once.
        store.impose(new Alldifferent(x));

        // For each set j, the number of positions i where the set's digit equals x[i]
        // is exactly k. match[j][i] is 1 when x[i] equals the set's digit in position i.
        for (int j = 0; j < numSets; j++) {
            JSONArray set = sets.getJSONArray(j);
            IntVar[] match = new IntVar[n];
            int[] ones = new int[n];
            for (int i = 0; i < n; i++) {
                BooleanVar b = new BooleanVar(store, "m" + j + "_" + i);
                store.impose(new Reified(new XeqC(x[i], set.getInt(i)), b));
                match[i] = b;
                ones[i] = 1;
            }
            // Exactly k positions agree with this set.
            store.impose(new LinearInt(match, ones, "==", k));
        }

        // Output x is the account number. Label its digits first.
        return new Model().put("x", x).search(x, null, null);
    }
}
