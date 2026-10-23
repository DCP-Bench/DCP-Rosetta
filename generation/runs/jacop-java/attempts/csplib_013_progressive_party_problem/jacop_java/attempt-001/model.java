// Progressive party problem (CSPLib 013): timetable a yacht-club party.
// Some boats are hosts; the crews of the other (guest) boats visit host boats
// over several half-hour periods. Hosts keep their crew on board. Minimise the
// number of host boats.
//
// Variables:
//   host[b]        1 if boat b is a host (is_host).
//   visits[p][b]   the boat that boat b is aboard, in period p. A host boat
//                  visits itself in every period; a guest boat visits a host.
//   occ[p][b][v]   1 if visits[p][b] == v (boolean view of visits).
//
// Constraints, in the problem's own terms:
//   - a boat is a host exactly when it stays at itself in every period;
//   - a guest boat can only visit a boat that is a host (occ <= host[v]);
//   - a guest boat cannot revisit a host: it visits each host at most once;
//   - the people aboard a host in a period, its own crew plus the guest crews
//     visiting it, do not exceed its capacity;
//   - two crews meet when they are aboard the same host in the same period;
//     two crews meet at most once over all periods;
//   - objective: the number of host boats.
//
// Sizes come from the instance: n_boats boats, n_periods periods, the
// capacity and crew_size of each boat. Nothing here depends on the example.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XeqY;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n_boats");
        int periods = inst.getInt("n_periods");
        JSONArray capJson = inst.getJSONArray("capacity");
        JSONArray crewJson = inst.getJSONArray("crew_size");

        int[] capacity = new int[n];
        int[] crew = new int[n];
        for (int b = 0; b < n; b++) {
            capacity[b] = capJson.getInt(b);
            crew[b] = crewJson.getInt(b);
        }

        // Host indicator per boat.
        BooleanVar[] host = new BooleanVar[n];
        for (int b = 0; b < n; b++) {
            host[b] = new BooleanVar(store);
        }

        // Which boat each boat is aboard, per period (0-based boat indices).
        IntVar[][] visits = new IntVar[periods][n];
        for (int p = 0; p < periods; p++) {
            for (int b = 0; b < n; b++) {
                visits[p][b] = new IntVar(store, "visit_" + p + "_" + b, 0, n - 1);
            }
        }

        // occ[p][b][v] = 1 if boat b is aboard boat v in period p.
        BooleanVar[][][] occ = new BooleanVar[periods][n][n];
        for (int p = 0; p < periods; p++) {
            for (int b = 0; b < n; b++) {
                for (int v = 0; v < n; v++) {
                    occ[p][b][v] = new BooleanVar(store);
                    store.impose(new Reified(new XeqC(visits[p][b], v), occ[p][b][v]));
                }
            }
        }

        for (int p = 0; p < periods; p++) {
            for (int h = 0; h < n; h++) {
                // A host stays aboard itself: host[h] is 1 exactly when
                // boat h visits itself in period p.
                store.impose(new XeqY(occ[p][h][h], host[h]));

                // A guest can only visit a boat that is a host.
                for (int b = 0; b < n; b++) {
                    store.impose(new LinearInt(
                        new IntVar[]{occ[p][b][h], host[h]},
                        new int[]{1, -1}, "<=", 0));
                }
            }

            // Capacity of each boat in each period: the crews aboard it,
            // its own crew included when it is a host, fit its capacity.
            for (int h = 0; h < n; h++) {
                IntVar[] aboard = new IntVar[n];
                int[] sizes = new int[n];
                for (int b = 0; b < n; b++) {
                    aboard[b] = occ[p][b][h];
                    sizes[b] = crew[b];
                }
                store.impose(new LinearInt(aboard, sizes, "<=", capacity[h]));
            }
        }

        // A guest boat cannot revisit a host: in two periods p < q it is aboard
        // the same boat v only if it is itself a host (then v = itself).
        for (int b = 0; b < n; b++) {
            for (int p = 0; p < periods; p++) {
                for (int q = p + 1; q < periods; q++) {
                    for (int v = 0; v < n; v++) {
                        store.impose(new LinearInt(
                            new IntVar[]{occ[p][b][v], occ[q][b][v], host[b]},
                            new int[]{1, 1, -1}, "<=", 1));
                    }
                }
            }
        }

        // Two crews meet when they are aboard the same boat in the same period.
        // Any two crews meet at most once over all periods.
        for (int g1 = 0; g1 < n; g1++) {
            for (int g2 = g1 + 1; g2 < n; g2++) {
                IntVar[] meetings = new IntVar[periods];
                int[] ones = new int[periods];
                for (int p = 0; p < periods; p++) {
                    BooleanVar meet = new BooleanVar(store);
                    store.impose(new Reified(new XeqY(visits[p][g1], visits[p][g2]), meet));
                    meetings[p] = meet;
                    ones[p] = 1;
                }
                store.impose(new LinearInt(meetings, ones, "<=", 1));
            }
        }

        // Objective: number of host boats.
        IntVar hostCount = new IntVar(store, "hosts", 0, n);
        store.impose(new SumInt(host, "==", hostCount));

        Model m = new Model().put("is_host", host).put("visits", visits);
        return m.minimize(hostCount);
    }
}
