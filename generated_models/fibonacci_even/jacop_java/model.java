// Sum of the even-valued terms of the Fibonacci sequence 1, 2, 3, 5, 8, ... that do not exceed
// four million. Output: res = that sum.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Problem constants: the bound is four million, and the sequence starts 1, 2.
        int limit = 4000000;
        // The number of terms not exceeding the limit is 32 (the 32nd term is 3524578; the
        // next one, 5702887, is over the limit). The array holds exactly these terms.
        int numTerms = 32;

        // t[k] = k-th term of the sequence (0-based): t[0] = 1, t[1] = 2, t[k] = t[k-1] + t[k-2].
        IntVar[] t = new IntVar[numTerms];
        for (int k = 0; k < numTerms; k++) {
            t[k] = new IntVar(store, "t" + k, 1, limit);
        }
        store.impose(new LinearInt(new IntVar[]{t[0]}, new int[]{1}, "==", 1));
        store.impose(new LinearInt(new IntVar[]{t[1]}, new int[]{1}, "==", 2));
        for (int k = 2; k < numTerms; k++) {
            store.impose(new XplusYeqZ(t[k - 2], t[k - 1], t[k]));
        }

        // Parity of each term: t[k] = 2*q[k] + odd[k], with odd[k] in {0, 1}.
        // The term is even exactly when odd[k] = 0, so even[k] = 1 - odd[k].
        BooleanVar[] even = new BooleanVar[numTerms];
        IntVar[] evenValue = new IntVar[numTerms];
        for (int k = 0; k < numTerms; k++) {
            IntVar q = new IntVar(store, "q" + k, 0, limit / 2);
            // even[k] = 1 when t[k] is even. t[k] = 2*q[k] + 1 - even[k], so
            // 2*q[k] - t[k] - even[k] = -1.
            even[k] = new BooleanVar(store, "even" + k);
            store.impose(new LinearInt(new IntVar[]{q, t[k], even[k]},
                    new int[]{2, -1, -1}, "==", -1));

            // evenValue[k] = t[k] when the term is even, 0 otherwise.
            evenValue[k] = new IntVar(store, "ev" + k, 0, limit);
            store.impose(new XmulYeqZ(t[k], even[k], evenValue[k]));
        }

        // res = sum of the even terms.
        IntVar res = new IntVar(store, "res", 0, 10 * limit);
        store.impose(new SumInt(evenValue, "==", res));

        return new Model().put("res", res);
    }
}
