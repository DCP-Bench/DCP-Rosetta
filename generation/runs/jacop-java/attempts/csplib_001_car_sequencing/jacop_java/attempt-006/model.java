// Car sequencing: order the cars of a production run on one assembly line.
// sequence[p] is the car type (0-based) built in slot p. Each car type c must
// appear demand[c] times, and for every option o, any window of per_slots[o]
// consecutive slots may contain at most at_most[o] cars that require option o.
// Encoding: at[p][c] = 1 when slot p holds car type c (channelled to sequence).
import org.jacop.constraints.GCC;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.search.IndomainMin;
import org.jacop.search.SmallestDomain;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Sizes come from the instance: one car type per entry of demand,
        // one option per entry of at_most, and one slot per car.
        JSONArray demandJ = inst.getJSONArray("demand");
        JSONArray atMostJ = inst.getJSONArray("at_most");
        JSONArray perSlotsJ = inst.getJSONArray("per_slots");
        JSONArray requiresJ = inst.getJSONArray("requires");

        int types = demandJ.length();
        int options = atMostJ.length();
        int[] demand = new int[types];
        int total = 0;
        for (int c = 0; c < types; c++) {
            demand[c] = demandJ.getInt(c);
            total += demand[c];
        }

        // requires[c][o] = 1 if car type c needs option o.
        int[][] requires = new int[types][options];
        for (int c = 0; c < types; c++) {
            JSONArray row = requiresJ.getJSONArray(c);
            for (int o = 0; o < options; o++) {
                requires[c][o] = row.getInt(o);
            }
        }

        // sequence[p] = car type in slot p, 0-based.
        IntVar[] sequence = new IntVar[total];
        for (int p = 0; p < total; p++) {
            sequence[p] = new IntVar(store, "seq" + p, 0, types - 1);
        }

        // Production counts: each car type c occurs exactly demand[c] times.
        IntVar[] counters = new IntVar[types];
        for (int c = 0; c < types; c++) {
            counters[c] = new IntVar(store, demand[c], demand[c]);
        }
        store.impose(new GCC(sequence, counters));

        // at[p][c] = 1 exactly when slot p holds car type c. Each slot holds
        // exactly one car type, so the row sums to 1.
        BooleanVar[][] at = new BooleanVar[total][types];
        for (int p = 0; p < total; p++) {
            IntVar[] row = new IntVar[types];
            int[] ones = new int[types];
            for (int c = 0; c < types; c++) {
                at[p][c] = new BooleanVar(store, "at" + p + "_" + c);
                store.impose(new Reified(new XeqC(sequence[p], c), at[p][c]));
                row[c] = at[p][c];
                ones[c] = 1;
            }
            store.impose(new LinearInt(row, ones, "==", 1));
        }

        // Types that require option o, listed once per option.
        int[][] needing = new int[options][];
        for (int o = 0; o < options; o++) {
            int count = 0;
            for (int c = 0; c < types; c++) {
                count += requires[c][o];
            }
            needing[o] = new int[count];
            int k = 0;
            for (int c = 0; c < types; c++) {
                if (requires[c][o] == 1) {
                    needing[o][k++] = c;
                }
            }
        }

        // Implied total: over the whole line, the cars requiring option o number
        // exactly the sum of demand[c] over the types c that require o. This is
        // implied by the counts above, and gives the window constraints a tight
        // bound on the total.
        for (int o = 0; o < options; o++) {
            if (needing[o].length == 0) continue; // no car needs o: nothing to bound
            int required = 0;
            for (int c = 0; c < types; c++) {
                required += demand[c] * requires[c][o];
            }
            IntVar[] all = new IntVar[total * needing[o].length];
            int[] ones = new int[all.length];
            int k = 0;
            for (int p = 0; p < total; p++) {
                for (int c : needing[o]) {
                    all[k] = at[p][c];
                    ones[k] = 1;
                    k++;
                }
            }
            store.impose(new LinearInt(all, ones, "==", required));
        }

        // Capacity: in every window of per_slots[o] consecutive slots, at most
        // at_most[o] cars require option o. Only full windows inside the line
        // are posted.
        for (int o = 0; o < options; o++) {
            if (needing[o].length == 0) continue; // no car needs o: nothing to bound
            int window = perSlotsJ.getInt(o);
            int limit = atMostJ.getInt(o);
            for (int start = 0; start + window <= total; start++) {
                IntVar[] inWindow = new IntVar[window * needing[o].length];
                int[] ones = new int[inWindow.length];
                int k = 0;
                for (int q = start; q < start + window; q++) {
                    for (int c : needing[o]) {
                        inWindow[k] = at[q][c];
                        ones[k] = 1;
                        k++;
                    }
                }
                store.impose(new LinearInt(inWindow, ones, "<=", limit));
            }
        }

        // Search: label the slots first, most constrained slot first (smallest
        // domain), lowest car type first. The runner's default order (smallest
        // domain first over every variable) would pick the 0/1 channel variables
        // before the slots and thrash. The runner still labels the rest afterwards.
        return new Model().put("sequence", sequence)
                .search(sequence, new SmallestDomain<IntVar>(), new IndomainMin<IntVar>());
    }
}
