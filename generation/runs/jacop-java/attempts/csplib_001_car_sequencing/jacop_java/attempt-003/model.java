// Car sequencing: order the cars of a production run on one assembly line.
// sequence[p] is the car type (0-based) built in slot p. Each car type c must
// appear demand[c] times, and for every option o, any window of per_slots[o]
// consecutive slots may contain at most at_most[o] cars that require option o.
import org.jacop.constraints.Element;
import org.jacop.constraints.GCC;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
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
        // GCC is the global cardinality constraint, stronger than one Count per type.
        IntVar[] counters = new IntVar[types];
        for (int c = 0; c < types; c++) {
            counters[c] = new IntVar(store, demand[c], demand[c]);
        }
        store.impose(new GCC(sequence, counters));

        // need[p][o] = 1 if the car in slot p requires option o.
        // It is read off the requires table through the slot's car type.
        IntVar[][] need = new IntVar[total][options];
        for (int o = 0; o < options; o++) {
            int[] column = new int[types];
            for (int c = 0; c < types; c++) {
                column[c] = requires[c][o];
            }
            for (int p = 0; p < total; p++) {
                need[p][o] = new IntVar(store, "need" + p + "_" + o, 0, 1);
                // offset -1: the index (car type) is 0-based.
                store.impose(Element.choose(sequence[p], column, need[p][o], -1));
            }
        }

        // Implied total: the cars requiring option o over the whole line number
        // exactly the sum of demand[c] over the types c that require o. Each
        // type appears demand[c] times, so this holds for every sequence.
        for (int o = 0; o < options; o++) {
            int required = 0;
            for (int c = 0; c < types; c++) {
                required += demand[c] * requires[c][o];
            }
            IntVar[] column = new IntVar[total];
            int[] ones = new int[total];
            for (int p = 0; p < total; p++) {
                column[p] = need[p][o];
                ones[p] = 1;
            }
            store.impose(new LinearInt(column, ones, "==", required));
        }

        // Capacity: in every window of per_slots[o] consecutive slots, at most
        // at_most[o] cars require option o. Only full windows inside the line
        // are posted.
        for (int o = 0; o < options; o++) {
            int window = perSlotsJ.getInt(o);
            int limit = atMostJ.getInt(o);
            for (int start = 0; start + window <= total; start++) {
                IntVar[] inWindow = new IntVar[window];
                int[] ones = new int[window];
                for (int k = 0; k < window; k++) {
                    inWindow[k] = need[start + k][o];
                    ones[k] = 1;
                }
                store.impose(new LinearInt(inWindow, ones, "<=", limit));
            }
        }

        // The declared output is the sequence of car types.
        return new Model().put("sequence", sequence);
    }
}
