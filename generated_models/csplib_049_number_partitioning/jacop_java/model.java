// Number partitioning: split the numbers 1..n into two sets A and B of equal size (n/2 each) with
// equal sums and equal sums of squares. Outputs "A" and "B" are arrays of n/2 values from 1..n.
// The instances have even n. The model has a Boolean per value (inA[v] = 1 if v is in A), so the
// cardinality, sum and sum-of-squares conditions are linear over those Booleans and propagate well.
// The slot variables A[k] and B[k] are linked to the Booleans by reified equalities.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        int h = n / 2; // size of each set

        // inA[v-1] = 1 if the number v (1..n) belongs to A, 0 if it belongs to B.
        BooleanVar[] inA = new BooleanVar[n];
        for (int v = 1; v <= n; v++) {
            inA[v - 1] = new BooleanVar(store, "inA_" + v);
        }

        // Slots: a[k] is the k-th number of A and b[k] the k-th number of B. All n slots together
        // hold 1..n exactly once.
        IntVar[] a = new IntVar[h];
        IntVar[] b = new IntVar[h];
        IntVar[] all = new IntVar[n];
        for (int k = 0; k < h; k++) {
            a[k] = new IntVar(store, "A_" + k, 1, n);
            all[k] = a[k];
        }
        for (int k = 0; k < h; k++) {
            b[k] = new IntVar(store, "B_" + k, 1, n);
            all[h + k] = b[k];
        }
        store.impose(new Alldifferent(all));

        // Link the slots to the Booleans. eA[k][v-1] = 1 iff A[k] = v; fB[k][v-1] = 1 iff B[k] = v.
        BooleanVar[][] eA = new BooleanVar[h][n];
        BooleanVar[][] fB = new BooleanVar[h][n];
        for (int k = 0; k < h; k++) {
            for (int v = 1; v <= n; v++) {
                eA[k][v - 1] = new BooleanVar(store, "eA_" + k + "_" + v);
                store.impose(new Reified(new XeqC(a[k], v), eA[k][v - 1]));
                fB[k][v - 1] = new BooleanVar(store, "fB_" + k + "_" + v);
                store.impose(new Reified(new XeqC(b[k], v), fB[k][v - 1]));
            }
        }

        // Value v sits in A exactly when inA[v] = 1: one A slot holds it if it is in A, and one
        // B slot holds it otherwise. So sum_k eA[k][v] = inA[v] and sum_k fB[k][v] = 1 - inA[v].
        for (int v = 1; v <= n; v++) {
            IntVar[] inASlots = new IntVar[h + 1];
            int[] inAWeights = new int[h + 1];
            for (int k = 0; k < h; k++) {
                inASlots[k] = eA[k][v - 1];
                inAWeights[k] = 1;
            }
            inASlots[h] = inA[v - 1];
            inAWeights[h] = -1;
            store.impose(new LinearInt(inASlots, inAWeights, "==", 0));

            IntVar[] inBSlots = new IntVar[h + 1];
            int[] inBWeights = new int[h + 1];
            for (int k = 0; k < h; k++) {
                inBSlots[k] = fB[k][v - 1];
                inBWeights[k] = 1;
            }
            inBSlots[h] = inA[v - 1];
            inBWeights[h] = 1;
            store.impose(new LinearInt(inBSlots, inBWeights, "==", 1));
        }

        // Equal cardinality: |A| = n/2, so the Booleans for A sum to n/2.
        IntVar[] members = new IntVar[n];
        int[] ones = new int[n];
        for (int v = 0; v < n; v++) {
            members[v] = inA[v];
            ones[v] = 1;
        }
        store.impose(new LinearInt(members, ones, "==", h));

        // Equal sums: sum(A) = sum(B) = n(n+1)/4, which is 2*sum(A) = n(n+1)/2 in linear form.
        int[] twoV = new int[n];
        int[] twoVSquared = new int[n];
        for (int v = 1; v <= n; v++) {
            twoV[v - 1] = 2 * v;
            twoVSquared[v - 1] = 2 * v * v;
        }
        store.impose(new LinearInt(members, twoV, "==", n * (n + 1) / 2));

        // Equal sums of squares: 2 * sum over A of v^2 = sum over 1..n of v^2 = n(n+1)(2n+1)/6.
        store.impose(new LinearInt(members, twoVSquared, "==", n * (n + 1) * (2 * n + 1) / 6));

        // Decisions: the membership Booleans first, then the slots.
        IntVar[] order = new IntVar[n + n];
        for (int v = 0; v < n; v++) {
            order[v] = inA[v];
        }
        for (int i = 0; i < n; i++) {
            order[n + i] = all[i];
        }
        return new Model().put("A", a).put("B", b).search(order, null, null);
    }
}
