// Bales of hay: find the weight of each of n bales, given the weights of all pairs of bales
// (the list of pairwise sums, in sorted order, without saying which pair gave which sum).
// bales[i] = weight of bale i. The multiset of sums bales[i] + bales[j] over all pairs i < j
// must be exactly the given list of weights.

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
        int n = inst.getInt("n");                       // number of bales, from the instance
        JSONArray w = inst.getJSONArray("weights");     // the pairwise sums, n*(n-1)/2 of them
        int pairs = w.length();

        // the largest given sum bounds every bale weight (weights are not negative)
        int maxW = 0;
        for (int k = 0; k < pairs; k++) maxW = Math.max(maxW, w.getInt(k));

        // bales[i] in 0..maxW
        IntVar[] bales = new IntVar[n];
        for (int i = 0; i < n; i++) {
            bales[i] = new IntVar(store, "bale" + i, 0, maxW);
        }

        // s[p] = weight of the pair p of bales, for the pairs (i, j) with i < j, in a fixed order
        IntVar[] s = new IntVar[pairs];
        int p = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                s[p] = new IntVar(store, "pair" + i + "_" + j, 0, 2 * maxW);
                // s = bales[i] + bales[j]
                store.impose(new org.jacop.constraints.XplusYeqZ(bales[i], bales[j], s[p]));
                p++;
            }
        }

        // Each pair sum must equal one of the given weights. hit[p][v] = 1 if pair p has the
        // v-th distinct given weight value. Exactly one value per pair.
        int[] distinct = new int[pairs];
        int distinctCount = 0;
        for (int k = 0; k < pairs; k++) {
            if (k == 0 || w.getInt(k) != w.getInt(k - 1)) {
                distinct[distinctCount++] = w.getInt(k);
            }
        }

        int[] ones = new int[distinctCount];
        java.util.Arrays.fill(ones, 1);
        int[] onesP = new int[pairs];
        java.util.Arrays.fill(onesP, 1);

        // hit[p][v] = 1 when pair sum p equals distinct value v
        BooleanVar[][] hit = new BooleanVar[pairs][distinctCount];
        for (int q = 0; q < pairs; q++) {
            for (int v = 0; v < distinctCount; v++) {
                hit[q][v] = new BooleanVar(store, "hit" + q + "_" + v);
                store.impose(new Reified(new XeqC(s[q], distinct[v]), hit[q][v]));
            }
            // every pair sum takes exactly one of the given values
            store.impose(new LinearInt(hit[q], ones, "==", 1));
        }

        // the multiset matches: for each given value v, the number of pairs with that sum
        // equals how many times v appears in the list of weights
        for (int v = 0; v < distinctCount; v++) {
            int count = 0;
            for (int k = 0; k < pairs; k++) {
                if (w.getInt(k) == distinct[v]) count++;
            }
            BooleanVar[] column = new BooleanVar[pairs];
            for (int q = 0; q < pairs; q++) column[q] = hit[q][v];
            store.impose(new LinearInt(column, onesP, "==", count));
        }

        Model model = new Model().put("bales", bales);
        return model;
    }
}
