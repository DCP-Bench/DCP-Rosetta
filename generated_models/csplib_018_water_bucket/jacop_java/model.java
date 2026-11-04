// Water bucket problem: three buckets with capacities, pour water between them to go from
// the initial state to the goal state in as few transfers as possible.
// sequence[t] is the state of the three buckets after t transfers (sequence[0] = initial state).
// After the goal state is reached, the remaining entries are the padding state.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.table.Table;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;
import java.util.ArrayList;
import java.util.List;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        // Everything below comes from the instance: capacities, start and goal states,
        // the number of states in the sequence and the padding value.
        int steps = instance.getInt("MAX_STEPS");
        int pad = instance.getInt("PADDING_VALUE");
        int[] cap = toArray(instance.getJSONArray("capacities"));
        int[] init = toArray(instance.getJSONArray("initial_state"));
        int[] goal = toArray(instance.getJSONArray("goal_state"));
        int buckets = cap.length;

        int total = 0;
        int maxCap = 0;
        for (int b = 0; b < buckets; b++) {
            total += init[b];
            maxCap = Math.max(maxCap, cap[b]);
        }

        // All legal states: each bucket within its capacity, total water conserved.
        List<int[]> states = new ArrayList<>();
        enumerateStates(cap, total, new int[buckets], 0, states);

        // s[t][b] = content of bucket b after t transfers. Real states take values in
        // 0..maxCap; a padding state has every entry equal to pad.
        IntVar[][] s = new IntVar[steps][buckets];
        for (int t = 0; t < steps; t++) {
            for (int b = 0; b < buckets; b++) {
                if (t == 0) {
                    s[t][b] = new IntVar(store, "s" + t + "_" + b, init[b], init[b]);
                } else {
                    s[t][b] = new IntVar(store, "s" + t + "_" + b, Math.min(pad, 0), maxCap);
                }
            }
        }

        // a[t] = 1 if transfer t+1 is a real pour; a[t] = 0 once the goal has been reached
        // (the transition from the goal state to padding, and padding stays padding).
        BooleanVar[] a = new BooleanVar[steps - 1];
        for (int t = 0; t < steps - 1; t++) {
            a[t] = new BooleanVar(store, "pour" + t);
        }

        // Transition table for each step: (state before, state after, real pour flag).
        // A real pour moves water from one bucket to another without overflowing or emptying
        // past zero (the amount is the smaller of what the source holds and what the target
        // has room for). A non-pour is allowed only from the goal state or from padding,
        // and leads to padding.
        int[][] pourTuples = pourTuples(states, cap, goal, pad, buckets);
        for (int t = 0; t < steps - 1; t++) {
            IntVar[] row = new IntVar[2 * buckets + 1];
            for (int b = 0; b < buckets; b++) {
                row[b] = s[t][b];
                row[buckets + b] = s[t + 1][b];
            }
            row[2 * buckets] = a[t];
            store.impose(new Table(row, pourTuples));
        }

        // The sequence has to end in the goal state or in padding, so the goal is reached
        // within MAX_STEPS states.
        int[][] endStates = new int[2][buckets];
        for (int b = 0; b < buckets; b++) {
            endStates[0][b] = goal[b];
            endStates[1][b] = pad;
        }
        store.impose(new Table(s[steps - 1], endStates));

        // cost = number of real transfers = sum of a[t].
        IntVar cost = new IntVar(store, "cost", 0, steps - 1);
        IntVar[] terms = new IntVar[steps];
        int[] weights = new int[steps];
        for (int t = 0; t < steps - 1; t++) {
            terms[t] = a[t];
            weights[t] = 1;
        }
        terms[steps - 1] = cost;
        weights[steps - 1] = -1;
        store.impose(new LinearInt(terms, weights, "==", 0));

        // Decision variables: the pour flags first, then the states.
        List<IntVar> order = new ArrayList<>();
        for (BooleanVar v : a) {
            order.add(v);
        }
        for (int t = 1; t < steps; t++) {
            for (int b = 0; b < buckets; b++) {
                order.add(s[t][b]);
            }
        }

        Model m = new Model().put("cost", cost).put("sequence", s);
        m.search(order.toArray(new IntVar[0]), null, null);
        return m.minimize(cost);
    }

    // Lists the states (x_0, ..., x_{k-1}) with 0 <= x_b <= cap[b] and sum equal to total.
    private static void enumerateStates(int[] cap, int total, int[] cur, int b, List<int[]> out) {
        if (b == cap.length) {
            if (total == 0) {
                out.add(cur.clone());
            }
            return;
        }
        for (int v = 0; v <= cap[b] && v <= total; v++) {
            cur[b] = v;
            enumerateStates(cap, total - v, cur, b + 1, out);
        }
    }

    // Tuples (before, after, pour) for the table: every pour between two buckets that moves
    // a positive amount, plus the stop transitions from the goal and from padding.
    private static int[][] pourTuples(List<int[]> states, int[] cap, int[] goal, int pad, int buckets) {
        List<int[]> tuples = new ArrayList<>();
        for (int[] st : states) {
            for (int from = 0; from < buckets; from++) {
                for (int to = 0; to < buckets; to++) {
                    if (from == to) {
                        continue;
                    }
                    int amount = Math.min(st[from], cap[to] - st[to]);
                    if (amount <= 0) {
                        continue;
                    }
                    int[] next = st.clone();
                    next[from] -= amount;
                    next[to] += amount;
                    int[] row = new int[2 * buckets + 1];
                    System.arraycopy(st, 0, row, 0, buckets);
                    System.arraycopy(next, 0, row, buckets, buckets);
                    row[2 * buckets] = 1;
                    tuples.add(row);
                }
            }
        }
        // Stop from the goal state to padding.
        int[] goalToPad = new int[2 * buckets + 1];
        System.arraycopy(goal, 0, goalToPad, 0, buckets);
        for (int b = 0; b < buckets; b++) {
            goalToPad[buckets + b] = pad;
        }
        tuples.add(goalToPad);
        // Padding stays padding.
        int[] padToPad = new int[2 * buckets + 1];
        for (int b = 0; b < 2 * buckets; b++) {
            padToPad[b] = pad;
        }
        tuples.add(padToPad);
        return tuples.toArray(new int[0][]);
    }

    private static int[] toArray(JSONArray arr) {
        int[] out = new int[arr.length()];
        for (int i = 0; i < out.length; i++) {
            out[i] = arr.getInt(i);
        }
        return out;
    }
}
