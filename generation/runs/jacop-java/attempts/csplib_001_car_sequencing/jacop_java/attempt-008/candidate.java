// Car sequencing: order the cars of a production run on one assembly line.
// sequence[p] is the car type (0-based) built in slot p. Car type c occurs
// demand[c] times, and for every option o any window of per_slots[o]
// consecutive slots holds at most at_most[o] cars that require o.
//
// Encoding: each slot has a rank variable. Rank 0 is the car type that needs
// the most heavily loaded options, so the search (slots left to right, smallest
// rank first) places the hardest cars first. The rank is mapped back to the car
// type for the declared output. Per option, a 0/1 variable per slot says whether
// the slot's car needs the option; Sequence enforces the window rule on it, and
// implied prefix bounds (valid consequences of the rule and the demands) help
// propagation.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.*;
import java.util.*;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray dj = inst.getJSONArray("demand");
        JSONArray aj = inst.getJSONArray("at_most");
        JSONArray qj = inst.getJSONArray("per_slots");
        JSONArray rj = inst.getJSONArray("requires");
        int C = dj.length(), O = aj.length(), n = 0;
        int[] demand = new int[C], atMost = new int[O], perSlots = new int[O];
        int[][] req = new int[C][O];
        for (int c = 0; c < C; c++) {
            demand[c] = dj.getInt(c);
            n += demand[c];
            for (int o = 0; o < O; o++) req[c][o] = rj.getJSONArray(c).getInt(o);
        }
        for (int o = 0; o < O; o++) { atMost[o] = aj.getInt(o); perSlots[o] = qj.getInt(o); }

        // Load of option o: cars needing it, scaled by window/capacity, over the line length.
        double[] util = new double[O];
        int[] need = new int[O];
        for (int o = 0; o < O; o++) {
            for (int c = 0; c < C; c++) need[o] += req[c][o] * demand[c];
            util[o] = (double) need[o] * perSlots[o] / ((double) atMost[o] * n);
        }
        // Options by decreasing load; car types sorted so those needing the
        // most loaded options come first (rank 0 = first).
        Integer[] oo = new Integer[O];
        for (int o = 0; o < O; o++) oo[o] = o;
        Arrays.sort(oo, (a, b) -> Double.compare(util[b], util[a]));
        Integer[] ord = new Integer[C];
        for (int c = 0; c < C; c++) ord[c] = c;
        Arrays.sort(ord, (a, b) -> {
            for (int o : oo) if (req[a][o] != req[b][o]) return req[b][o] - req[a][o];
            return 0;
        });
        int[] order = new int[C];
        for (int r = 0; r < C; r++) order[r] = ord[r];

        IntVar[] rank = new IntVar[n], seq = new IntVar[n];
        for (int p = 0; p < n; p++) rank[p] = new IntVar(store, "r" + p, 0, C - 1);
        // Demand: rank r (type order[r]) occurs demand[order[r]] times.
        IntVar[] cnt = new IntVar[C];
        for (int r = 0; r < C; r++) cnt[r] = new IntVar(store, demand[order[r]], demand[order[r]]);
        store.impose(new GCC(rank, cnt));
        // Output: the car type of each slot (Element is 1-based, offset -1).
        for (int p = 0; p < n; p++) {
            seq[p] = new IntVar(store, "t" + p, 0, C - 1);
            store.impose(Element.choose(rank[p], order, seq[p], -1));
        }

        for (int o = 0; o < O; o++) {
            int[] col = new int[C];
            for (int r = 0; r < C; r++) col[r] = req[order[r]][o];
            IntVar[] nd = new IntVar[n]; // nd[p] = 1 iff slot p's car needs option o
            for (int p = 0; p < n; p++) {
                nd[p] = new IntVar(store, "n" + o + "_" + p, 0, 1);
                store.impose(Element.choose(rank[p], col, nd[p], -1));
            }
            // At most atMost[o] of any perSlots[o] consecutive slots. Sequence is
            // a decomposed constraint, hence imposeDecomposition.
            store.imposeDecomposition(new Sequence(nd, new IntervalDomain(1, 1), perSlots[o], 0, atMost[o]));
            // Implied bounds on prefixes: the first t slots hold at most `upper`
            // cars needing o, and the rest of the line can absorb only restUpper
            // of the need[o] cars, so at least need[o]-restUpper are in the prefix.
            int a = atMost[o], q = perSlots[o];
            for (int t = 1; t <= n; t++) {
                int upper = a * (t / q) + Math.min(a, t % q);
                int rest = n - t, restUpper = a * (rest / q) + Math.min(a, rest % q);
                int lower = need[o] - restUpper;
                IntVar[] pre = Arrays.copyOf(nd, t);
                int[] w = new int[t];
                Arrays.fill(w, 1);
                if (upper < t) store.impose(new LinearInt(pre, w, "<=", upper));
                if (lower > 0) store.impose(new LinearInt(pre, w, ">=", lower));
            }
        }
        // Label the ranks slot by slot, lowest rank first.
        return new Model().put("sequence", seq).search(rank, null, null);
    }
}
