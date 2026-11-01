// Bin packing: assign each item to one of num_bins bins of the given capacity, so that the
// total weight of the items in every bin does not exceed the capacity.
// bins[i] = index of the bin item i goes to (0-based).

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
        JSONArray wj = inst.getJSONArray("weights");   // item weights, from the instance
        int items = wj.length();
        int capacity = inst.getInt("capacity");        // capacity of every bin
        int numBins = inst.getInt("num_bins");         // number of available bins

        int[] w = new int[items];
        for (int i = 0; i < items; i++) w[i] = wj.getInt(i);

        // bins[i] in 0..numBins-1
        IntVar[] bins = new IntVar[items];
        for (int i = 0; i < items; i++) {
            bins[i] = new IntVar(store, "bin" + i, 0, numBins - 1);
        }

        // inBin[i][b] = 1 if item i is in bin b
        BooleanVar[][] inBin = new BooleanVar[items][numBins];
        for (int i = 0; i < items; i++) {
            for (int b = 0; b < numBins; b++) {
                inBin[i][b] = new BooleanVar(store, "in" + i + "_" + b);
                store.impose(new Reified(new XeqC(bins[i], b), inBin[i][b]));
            }
        }

        // capacity: for each bin, the weights of the items in it sum to at most the capacity
        for (int b = 0; b < numBins; b++) {
            BooleanVar[] column = new BooleanVar[items];
            for (int i = 0; i < items; i++) column[i] = inBin[i][b];
            store.impose(new LinearInt(column, w, "<=", capacity));
        }

        Model model = new Model().put("bins", bins);
        return model;
    }
}
