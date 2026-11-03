// Template design (CSPLib 002): print mother sheets for a family of design variations.
// Each template has n_slots slots, all filled: layout[t][v] is the number of slots on
// template t carrying variation v, and the row sums to n_slots. Template t is printed
// production[t] times. Each variation v needs at least demand[v] copies in total.
// Minimise the total number of sheets printed.
import org.jacop.constraints.*;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int slots = inst.getInt("n_slots");
        int templates = inst.getInt("n_templates");
        int variations = inst.getInt("n_var");
        JSONArray demandJson = inst.getJSONArray("demand");
        int[] demand = new int[variations];
        int totalDemand = 0, maxDemand = 0;
        for (int v = 0; v < variations; v++) {
            demand[v] = demandJson.getInt(v);
            totalDemand += demand[v];
            maxDemand = Math.max(maxDemand, demand[v]);
        }

        // layout[t][v]: slots of template t that carry variation v
        IntVar[][] layout = new IntVar[templates][variations];
        // production[t]: sheets printed from template t (never more than the largest demand)
        IntVar[] production = new IntVar[templates];
        // copies[t][v] = layout[t][v] * production[t]
        IntVar[][] copies = new IntVar[templates][variations];
        for (int t = 0; t < templates; t++) {
            production[t] = new IntVar(store, "production_" + t, 1, maxDemand);
            for (int v = 0; v < variations; v++) {
                layout[t][v] = new IntVar(store, "layout_" + t + "_" + v, 0, slots);
                copies[t][v] = new IntVar(store, "copies_" + t + "_" + v, 0, slots * maxDemand);
                store.impose(new XmulYeqZ(layout[t][v], production[t], copies[t][v]));
            }
        }

        // total sheets, bounded below by the capacity bound ceil(total demand / n_slots)
        int minTotal = (totalDemand + slots - 1) / slots;
        IntVar total = new IntVar(store, "total_sheets", minTotal, templates * maxDemand);
        store.impose(new SumInt(production, "==", total));

        // every template is completely filled, so it prints n_slots copies per sheet
        for (int t = 0; t < templates; t++) {
            store.impose(new SumInt(layout[t], "==", new IntVar(store, slots, slots)));
            IntVar[] row = new IntVar[variations + 1];
            int[] w = new int[variations + 1];
            for (int v = 0; v < variations; v++) { row[v] = copies[t][v]; w[v] = 1; }
            row[variations] = production[t];
            w[variations] = -slots;
            store.impose(new LinearInt(row, w, "==", 0));
        }

        // each variation meets its demand; implied upper bound: the other variations still
        // need their demand out of the n_slots * total copies printed overall
        for (int v = 0; v < variations; v++) {
            IntVar[] col = new IntVar[templates];
            int[] ones = new int[templates];
            for (int t = 0; t < templates; t++) { col[t] = copies[t][v]; ones[t] = 1; }
            store.impose(new LinearInt(col, ones, ">=", demand[v]));
            IntVar[] col2 = new IntVar[templates + 1];
            int[] w2 = new int[templates + 1];
            for (int t = 0; t < templates; t++) { col2[t] = copies[t][v]; w2[t] = 1; }
            col2[templates] = total;
            w2[templates] = -slots;
            store.impose(new LinearInt(col2, w2, "<=", -(totalDemand - demand[v])));
        }

        // templates are interchangeable: production non-increasing
        for (int t = 0; t + 1 < templates; t++)
            store.impose(new XgteqY(production[t], production[t + 1]));

        // search: layout cells in template-major order, then production
        IntVar[] order = new IntVar[templates * variations + templates];
        for (int t = 0; t < templates; t++)
            for (int v = 0; v < variations; v++) order[t * variations + v] = layout[t][v];
        for (int t = 0; t < templates; t++) order[templates * variations + t] = production[t];

        return new Model().put("layout", layout).put("production", production)
            .search(order, null, null).minimize(total);
    }
}
