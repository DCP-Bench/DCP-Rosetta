// Farmer and cows: cows are numbered 1..num_cows and cow c gives c units of milk. The farmer
// gives each of num_sons sons a set of cows, with cows_per_son[k] cows for son k, so that every
// son gets the same total milk. cow_assignments[c-1] is the son (0-based) that gets cow c.
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
        // Cow count, son count and the cows each son receives all come from the instance.
        int cows = inst.getInt("num_cows");
        int sons = inst.getInt("num_sons");
        JSONArray perSon = inst.getJSONArray("cows_per_son");

        // son[c] = the son that gets cow c+1, as a 0-based son index.
        IntVar[] son = new IntVar[cows];
        for (int c = 0; c < cows; c++) {
            son[c] = new IntVar(store, 0, sons - 1);
        }

        // in[c][k] = 1 when cow c+1 goes to son k. Each cow goes to exactly one son,
        // because son[c] has a single value.
        BooleanVar[][] in = new BooleanVar[cows][sons];
        for (int c = 0; c < cows; c++) {
            for (int k = 0; k < sons; k++) {
                in[c][k] = new BooleanVar(store);
                store.impose(new Reified(new XeqC(son[c], k), in[c][k]));
            }
        }

        // Each son receives exactly the number of cows the distribution gives him.
        for (int k = 0; k < sons; k++) {
            BooleanVar[] col = new BooleanVar[cows];
            int[] ones = new int[cows];
            for (int c = 0; c < cows; c++) {
                col[c] = in[c][k];
                ones[c] = 1;
            }
            store.impose(new LinearInt(castToIntVar(col), ones, "==", perSon.getInt(k)));
        }

        // Equal milk: the total milk is 1 + 2 + ... + num_cows, shared equally by the sons.
        // Cow c+1 gives c+1 units, so the weights are 1..num_cows.
        long total = (long) cows * (cows + 1) / 2;
        if (total % sons != 0) {
            // The milk cannot be shared equally; no assignment exists.
            store.impose(new XeqC(new IntVar(store, 0, 0), 1));
        } else {
            int share = (int) (total / sons);
            for (int k = 0; k < sons; k++) {
                BooleanVar[] col = new BooleanVar[cows];
                int[] milk = new int[cows];
                for (int c = 0; c < cows; c++) {
                    col[c] = in[c][k];
                    milk[c] = c + 1;
                }
                store.impose(new LinearInt(castToIntVar(col), milk, "==", share));
            }
        }

        // Output: the son of each cow. Labelling the son variables fixes everything else.
        Model m = new Model().put("cow_assignments", son);
        return m.search(son, null, null);
    }

    private static IntVar[] castToIntVar(BooleanVar[] vars) {
        IntVar[] out = new IntVar[vars.length];
        for (int i = 0; i < vars.length; i++) {
            out[i] = vars[i];
        }
        return out;
    }
}
