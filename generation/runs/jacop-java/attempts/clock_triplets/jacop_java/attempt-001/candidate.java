// Clock triplets: rearrange the numbers 1 to 12 around the face of a clock so that
// no three adjacent numbers (the clock is circular) have a sum above 21.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        final int n = 12;          // numbers on the clock face
        final int maxTriplet = 21; // the bound on the sum of any three adjacent numbers

        // x[i] is the number at position i of the clock, positions 0..11 in order
        IntVar[] x = new IntVar[n];
        for (int i = 0; i < n; i++) {
            x[i] = new IntVar(store, "x" + i, 1, n);
        }

        // each of the numbers 1 to 12 appears exactly once
        store.impose(new Alldifferent(x));

        // every triplet of adjacent positions (wrapping round the clock) sums to at most 21
        for (int i = 0; i < n; i++) {
            IntVar[] triplet = {x[i], x[(i + 1) % n], x[(i + 2) % n]};
            store.impose(new LinearInt(triplet, new int[]{1, 1, 1}, "<=", maxTriplet));
        }

        return new Model().put("x", x);
    }
}
