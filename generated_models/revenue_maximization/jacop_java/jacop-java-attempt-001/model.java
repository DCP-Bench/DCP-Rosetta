// Revenue management: sell packages of flight itineraries. Package p sells x[p] units, at most its
// estimated demand. Package p uses seats on leg l when delta[p][l] = 1; the seats of each leg are
// limited to available_seats[l]. Maximise the total revenue sum revenue[p] * x[p].
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray demand = inst.getJSONArray("demand");               // one entry per package
        JSONArray revenue = inst.getJSONArray("revenue");             // price per unit, per package
        JSONArray seats = inst.getJSONArray("available_seats");       // capacity, per leg
        JSONArray delta = inst.getJSONArray("delta");                 // delta[p][l] = 1 if package p uses leg l
        int P = demand.length();                                      // number of packages
        int L = seats.length();                                       // number of legs

        // packages_to_sell[p] = units of package p sold, between 0 and its demand
        IntVar[] x = new IntVar[P];
        for (int p = 0; p < P; p++)
            x[p] = new IntVar(store, "x" + p, 0, demand.getInt(p));

        // Seat capacity: for every leg, the seats reserved by the packages using it do not
        // exceed the seats available on that leg.
        for (int l = 0; l < L; l++) {
            int users = 0;
            for (int p = 0; p < P; p++)
                if (delta.getJSONArray(p).getInt(l) == 1)
                    users++;
            IntVar[] vars = new IntVar[users];
            int[] w = new int[users];
            int k = 0;
            for (int p = 0; p < P; p++)
                if (delta.getJSONArray(p).getInt(l) == 1) {
                    vars[k] = x[p];
                    w[k] = 1;
                    k++;
                }
            if (users > 0)
                store.impose(new LinearInt(vars, w, "<=", seats.getInt(l)));
        }

        // Total revenue = sum revenue[p] * x[p]
        int maxRevenue = 0;
        for (int p = 0; p < P; p++)
            maxRevenue += revenue.getInt(p) * demand.getInt(p);
        IntVar total = new IntVar(store, 0, maxRevenue);
        IntVar[] terms = new IntVar[P + 1];
        int[] w = new int[P + 1];
        for (int p = 0; p < P; p++) {
            terms[p] = x[p];
            w[p] = revenue.getInt(p);
        }
        terms[P] = total;
        w[P] = -1;
        store.impose(new LinearInt(terms, w, "==", 0));    // total - sum revenue[p] * x[p] = 0

        return new Model().put("packages_to_sell", x).put("max_revenue", total).maximize(total);
    }
}
