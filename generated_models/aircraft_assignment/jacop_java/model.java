// Aircraft assignment: assign aircraft of several types to routes so that every
// route's passenger demand is met, no type is over-used, and the total
// operational cost is minimal.
//
// Variables: alloc[t][r] is the number of aircraft of type t assigned to route r.
// T = number of aircraft types, R = number of routes, both read from the instance.
//
// Constraints, in the problem's own terms:
//   - availability: the aircraft of type t assigned over all routes do not exceed
//     the number of units of that type (sum over r of alloc[t][r] <= availability[t]);
//   - demand: the passenger capacity of the aircraft assigned to route r covers its
//     demand (sum over t of capabilities[t][r] * alloc[t][r] >= demand[r]);
//   - objective: the total operational cost, sum over t and r of
//     costs[t][r] * alloc[t][r], is minimised. The cost is tied to a variable.
//
// Sizes come from the instance: availability (types), demand (routes) and the
// matrices. Nothing here depends on the example.

import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray availJson = inst.getJSONArray("availability");
        JSONArray demandJson = inst.getJSONArray("demand");
        JSONArray capJson = inst.getJSONArray("capabilities");
        JSONArray costJson = inst.getJSONArray("costs");

        int types = availJson.length();
        int routes = demandJson.length();

        // Number of aircraft of type t on route r. Each type can use at most all of its units.
        IntVar[][] alloc = new IntVar[types][routes];
        int maxCost = 0;
        for (int t = 0; t < types; t++) {
            int avail = availJson.getInt(t);
            for (int r = 0; r < routes; r++) {
                alloc[t][r] = new IntVar(store, "a_" + t + "_" + r, 0, avail);
                maxCost += costJson.getJSONArray(t).getInt(r) * avail;
            }
        }

        // Availability: the units of each type, summed over routes, fit the fleet.
        for (int t = 0; t < types; t++) {
            int[] ones = new int[routes];
            java.util.Arrays.fill(ones, 1);
            store.impose(new LinearInt(alloc[t], ones, "<=", availJson.getInt(t)));
        }

        // Demand: the capacity assigned to each route covers its passenger demand.
        for (int r = 0; r < routes; r++) {
            IntVar[] onRoute = new IntVar[types];
            int[] capacity = new int[types];
            for (int t = 0; t < types; t++) {
                onRoute[t] = alloc[t][r];
                capacity[t] = capJson.getJSONArray(t).getInt(r);
            }
            store.impose(new LinearInt(onRoute, capacity, ">=", demandJson.getInt(r)));
        }

        // Objective: total operational cost, tied to a variable and minimised.
        IntVar cost = new IntVar(store, 0, maxCost);
        IntVar[] all = new IntVar[types * routes + 1];
        int[] weights = new int[types * routes + 1];
        int k = 0;
        for (int t = 0; t < types; t++) {
            for (int r = 0; r < routes; r++) {
                all[k] = alloc[t][r];
                weights[k] = costJson.getJSONArray(t).getInt(r);
                k++;
            }
        }
        all[k] = cost;
        weights[k] = -1;
        store.impose(new LinearInt(all, weights, "==", 0));

        // Output: allocation[t][r] for each type t and route r.
        Model m = new Model().put("allocation", alloc);
        return m.minimize(cost);
    }
}
