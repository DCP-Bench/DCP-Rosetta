// Bus scheduling: the day is split into T slots of 4 hours, cyclic (the last slot is followed by
// the first). Each bus works 8 successive hours, so a bus starting in slot t covers slots t and
// t+1 (mod T). x[t] is the number of buses that start in slot t. The number of buses on duty in
// slot t is x[t] + x[t-1] (mod T), and it must meet demands[t]. Minimise the total number of buses.
// T and the demands come from the instance field demands.
import org.jacop.constraints.SumInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    public static Model build(JSONObject inst, Store store) {
        JSONArray demands = inst.getJSONArray("demands");
        int slots = demands.length();

        int sumDemand = 0;
        for (int t = 0; t < slots; t++) sumDemand += demands.getInt(t);

        // x[t]: buses starting in slot t. No slot needs more starts than the total demand.
        IntVar[] x = new IntVar[slots];
        for (int t = 0; t < slots; t++)
            x[t] = new IntVar(store, "x_" + t, 0, sumDemand);

        // Buses on duty in slot t: those that started in slot t and in the slot before it
        // (cyclically). Together they must meet the demand of slot t.
        for (int t = 0; t < slots; t++) {
            int before = (t - 1 + slots) % slots;
            store.impose(new SumInt(new IntVar[]{x[t], x[before]}, ">=",
                                    new IntVar(store, demands.getInt(t), demands.getInt(t))));
        }

        // The objective: the total number of buses, which is the sum of the starts.
        IntVar total = new IntVar(store, 0, 2 * sumDemand);
        store.impose(new SumInt(x, "==", total));

        return new Model().put("x", x).minimize(total);
    }
}
