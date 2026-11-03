// Rehearsal order. Pieces of music are rehearsed one after another, slot 0 to
// n-1, each with its own duration. rehearsal[p][i] = 1 when player p plays piece i.
// A player arrives just before the first piece they play and leaves just after the
// last one, so they wait for every piece in between that they do not play.
// Minimise the total waiting time over all players.
//
// Encoding: pos[i] is the slot of piece i, and order[s] is the piece in slot s
// (order is the inverse of pos). C[s] is the start time of slot s. For a player
// with first slot f and last slot l, the time present is C[l+1] - C[f], and the
// waiting time is that minus the time the player plays.
import org.jacop.constraints.Alldistinct;
import org.jacop.constraints.Element;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Max;
import org.jacop.constraints.Min;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;
import java.util.ArrayList;
import java.util.List;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("num_pieces");
        int players = inst.getInt("num_players");
        JSONArray durJson = inst.getJSONArray("duration");
        JSONArray reh = inst.getJSONArray("rehearsal");

        int[] dur = new int[n];
        int total = 0;
        for (int i = 0; i < n; i++) {
            dur[i] = durJson.getInt(i);
            total += dur[i];
        }

        // pos[i] = slot of piece i; order[s] = piece in slot s (inverse of pos)
        IntVar[] pos = new IntVar[n];
        IntVar[] order = new IntVar[n];
        for (int i = 0; i < n; i++) {
            pos[i] = new IntVar(store, "pos" + i, 0, n - 1);
            order[i] = new IntVar(store, "order" + i, 0, n - 1);
        }
        store.impose(new Alldistinct(pos));
        for (int i = 0; i < n; i++) {
            // order[pos[i]] = i
            IntVar piece = new IntVar(store, i, i);
            store.impose(Element.choose(pos[i], order, piece, -1));
        }

        // duration of the piece in each slot, and the start time of each slot
        IntVar[] slotDur = new IntVar[n];
        IntVar[] start = new IntVar[n + 1];
        start[0] = new IntVar(store, 0, 0);
        for (int s = 0; s < n; s++) {
            slotDur[s] = new IntVar(store, 0, maxOf(dur));
            store.impose(Element.choose(order[s], dur, slotDur[s], -1));
            start[s + 1] = new IntVar(store, 0, total);
            // start[s+1] = start[s] + slotDur[s]
            store.impose(new LinearInt(new IntVar[]{start[s + 1], start[s], slotDur[s]},
                    new int[]{1, -1, -1}, "==", 0));
        }

        // for each player: first and last slot of their pieces, and the times they
        // are present; the waiting time is present time minus playing time
        List<IntVar> ends = new ArrayList<>();
        List<IntVar> begins = new ArrayList<>();
        int playTotal = 0;
        for (int p = 0; p < players; p++) {
            JSONArray row = reh.getJSONArray(p);
            List<IntVar> slots = new ArrayList<>();
            for (int i = 0; i < n; i++) {
                if (row.getInt(i) == 1) {
                    slots.add(pos[i]);
                    playTotal += dur[i];
                }
            }
            if (slots.isEmpty()) {
                continue;  // a player with no piece is never present
            }
            IntVar[] sl = slots.toArray(new IntVar[0]);

            // first and last slot of this player
            IntVar first = new IntVar(store, 0, n - 1);
            store.impose(new Min(sl, first));
            IntVar last = new IntVar(store, 0, n - 1);
            store.impose(new Max(sl, last));

            // present from the start of the first slot to the end of the last slot
            IntVar after = new IntVar(store, 1, n);   // last + 1, as a start index
            store.impose(new LinearInt(new IntVar[]{after, last},
                    new int[]{1, -1}, "==", 1));
            IntVar startTime = new IntVar(store, 0, total);
            store.impose(Element.choose(first, start, startTime, -1));
            IntVar endTime = new IntVar(store, 0, total);
            store.impose(Element.choose(after, start, endTime, -1));
            begins.add(startTime);
            ends.add(endTime);
        }

        // waiting = sum(end times) - sum(start times) - total playing time
        int nt = ends.size() + begins.size() + 1;
        IntVar[] vars = new IntVar[nt];
        int[] weights = new int[nt];
        int k = 0;
        for (IntVar e : ends) {
            vars[k] = e;
            weights[k++] = 1;
        }
        for (IntVar b : begins) {
            vars[k] = b;
            weights[k++] = -1;
        }
        IntVar wait = new IntVar(store, 0, total * players);
        vars[k] = wait;
        weights[k] = -1;
        store.impose(new LinearInt(vars, weights, "==", playTotal));

        return new Model().put("rehearsal_order", order).minimize(wait);
    }

    private static int maxOf(int[] a) {
        int m = 0;
        for (int v : a) {
            m = Math.max(m, v);
        }
        return m;
    }
}
