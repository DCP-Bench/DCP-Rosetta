// Car sequencing: order the cars of a production run on one assembly line.
// sequence[p] is the car type (0-based) built in slot p. Each car type c must
// appear demand[c] times, and for every option o, any window of per_slots[o]
// consecutive slots may contain at most at_most[o] cars that require option o.
// Encoding: at[p][r] = 1 when slot p holds the car type of rank r (channelled
// to the slot's rank variable), and the declared sequence maps ranks back to
// car types.
import org.jacop.constraints.Element;
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
        int[] typeDemand = new int[types];
        int total = 0;
        for (int c = 0; c < types; c++) {
            typeDemand[c] = demandJ.getInt(c);
            total += typeDemand[c];
        }

        // requiresType[c][o] = 1 if car type c needs option o.
        int[][] requiresType = new int[types][options];
        for (int c = 0; c < types; c++) {
            JSONArray row = requiresJ.getJSONArray(c);
            for (int o = 0; o < options; o++) {
                requiresType[c][o] = row.getInt(o);
            }
        }

        // Ranks: rank r stands for the car type order[r], with the types sorted by
        // demand, largest first (ties keep the input order). Labelling lowest rank
        // first then tries the types with the most cars to place first, which
        // prunes the window constraints earlier. This only changes the value
        // order; the declared output is still the car type.
        Integer[] byDemand = new Integer[types];
        for (int c = 0; c < types; c++) {
            byDemand[c] = c;
        }
        java.util.Arrays.sort(byDemand, (a, b) -> typeDemand[b] - typeDemand[a]);
        int[] order = new int[types];
        int[] demand = new int[types];
        int[][] requires = new int[types][options];
        for (int r = 0; r < types; r++) {
            order[r] = byDemand[r];
            demand[r] = typeDemand[order[r]];
            requires[r] = requiresType[order[r]];
        }

        // rank[p] = rank of the car in slot p.
        IntVar[] rank = new IntVar[total];
        for (int p = 0; p < total; p++) {
            rank[p] = new IntVar(store, "rank" + p, 0, types - 1);
        }

        // Production counts: each rank r occurs exactly demand[r] times.
        IntVar[] counters = new IntVar[types];
        for (int r = 0; r < types; r++) {
            counters[r] = new IntVar(store, demand[r], demand[r]);
        }
        store.impose(new GCC(rank, counters));

        // at[p][r] = 1 exactly when slot p holds rank r. Each slot holds one
        // rank, so the row sums to 1.
        BooleanVar[][] at = new BooleanVar[total][types];
        for (int p = 0; p < total; p++) {
            IntVar[] row = new IntVar[types];
            int[] ones = new int[types];
            for (int r = 0; r < types; r++) {
                at[p][r] = new BooleanVar(store, "at" + p + "_" + r);
                store.impose(new Reified(new XeqC(rank[p], r), at[p][r]));
                row[r] = at[p][r];
                ones[r] = 1;
            }
            store.impose(new LinearInt(row, ones, "==", 1));
        }

        // Ranks whose car type requires option o, listed once per option.
        int[][] needing = new int[options][];
        for (int o = 0; o < options; o++) {
            int count = 0;
            for (int r = 0; r < types; r++) {
                count += requires[r][o];
            }
            needing[o] = new int[count];
            int k = 0;
            for (int r = 0; r < types; r++) {
                if (requires[r][o] == 1) {
                    needing[o][k++] = r;
                }
            }
        }

        // Implied total: over the whole line, the cars requiring option o number
        // exactly the sum of demand over the car types that require o. This is
        // implied by the counts above and gives the window constraints a tight
        // bound on the total.
        for (int o = 0; o < options; o++) {
            if (needing[o].length == 0) continue; // no car needs o: nothing to bound
            int required = 0;
            for (int r = 0; r < types; r++) {
                required += demand[r] * requires[r][o];
            }
            IntVar[] all = new IntVar[total * needing[o].length];
            int[] ones = new int[all.length];
            int k = 0;
            for (int p = 0; p < total; p++) {
                for (int r : needing[o]) {
                    all[k] = at[p][r];
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
                    for (int r : needing[o]) {
                        inWindow[k] = at[q][r];
                        ones[k] = 1;
                        k++;
                    }
                }
                store.impose(new LinearInt(inWindow, ones, "<=", limit));
            }
        }

        // Declared output: slot p holds the car type order[rank[p]].
        IntVar[] sequence = new IntVar[total];
        for (int p = 0; p < total; p++) {
            sequence[p] = new IntVar(store, "type" + p, 0, types - 1);
            // offset -1: the rank is 0-based.
            store.impose(Element.choose(rank[p], order, sequence[p], -1));
        }

        // Search: label the slot ranks first, most constrained slot first
        // (smallest domain), lowest rank first. The runner's default order
        // (smallest domain first over every variable) would pick the 0/1 channel
        // variables before the slots and thrash. The runner labels the rest afterwards.
        return new Model().put("sequence", sequence)
                .search(rank, new SmallestDomain<IntVar>(), new IndomainMin<IntVar>());
    }
}
