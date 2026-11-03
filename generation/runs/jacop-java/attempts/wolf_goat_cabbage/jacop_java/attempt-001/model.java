// Wolf, goat and cabbage river crossing: a farmer takes a wolf, a goat and a cabbage across
// a river in a boat that carries the farmer and at most one item. Unattended, the wolf eats
// the goat and the goat eats the cabbage. Find a sequence of crossings, one stage per
// crossing, from everything on the starting shore (0) to everything on the destination
// shore (1). The number of stages comes from the instance; an odd count has no solution
// because the boat alternates shores and must end on the destination shore.
import org.jacop.constraints.Or;
import org.jacop.constraints.Reified;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XeqY;
import org.jacop.constraints.XneqY;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int stages = inst.getInt("stage");

        // shore of each item at each stage: 0 = starting shore, 1 = destination shore
        BooleanVar[] wolf = new BooleanVar[stages];
        BooleanVar[] goat = new BooleanVar[stages];
        BooleanVar[] cabbage = new BooleanVar[stages];
        // shore of the farmer's boat at each stage
        BooleanVar[] boat = new BooleanVar[stages];
        for (int t = 0; t < stages; t++) {
            wolf[t] = new BooleanVar(store, "wolf_" + t);
            goat[t] = new BooleanVar(store, "goat_" + t);
            cabbage[t] = new BooleanVar(store, "cabbage_" + t);
            boat[t] = new BooleanVar(store, "boat_" + t);
        }

        // start: everything on the starting shore; end: everything on the destination shore
        BooleanVar[][] items = {wolf, goat, cabbage};
        for (BooleanVar[] item : items) {
            store.impose(new XeqC(item[0], 0));
            store.impose(new XeqC(item[stages - 1], 1));
        }
        store.impose(new XeqC(boat[0], 0));
        store.impose(new XeqC(boat[stages - 1], 1));

        // each crossing: the boat changes shore, and the farmer goes along
        for (int t = 0; t + 1 < stages; t++) {
            store.impose(new XneqY(boat[t], boat[t + 1]));

            // an item that changes shore must be on the boat's shore before the crossing
            // (the farmer rows it across), so it must be on the same shore as the boat
            BooleanVar[] moved = new BooleanVar[items.length];
            int[] ones = new int[items.length];
            for (int k = 0; k < items.length; k++) {
                BooleanVar x = items[k][t];
                BooleanVar y = items[k][t + 1];
                store.impose(new Or(new XeqY(x, boat[t]), new XeqY(y, x)));

                // record whether this item crossed, for the one-item-per-trip limit
                moved[k] = new BooleanVar(store, "moved_" + k + "_" + t);
                store.impose(new Reified(new XneqY(x, y), moved[k]));
                ones[k] = 1;
            }
            // the boat carries the farmer and at most one item
            store.impose(new LinearInt(moved, ones, "<=", 1));
        }

        // safety at every stage: the wolf and the goat may share a shore only with the farmer;
        // the goat and the cabbage may share a shore only with the farmer
        for (int t = 0; t < stages; t++) {
            // if the wolf and goat are together, the farmer must be with them
            store.impose(new Or(new XneqY(wolf[t], goat[t]), new XeqY(boat[t], wolf[t])));
            // if the goat and cabbage are together, the farmer must be with them
            store.impose(new Or(new XneqY(goat[t], cabbage[t]), new XeqY(boat[t], goat[t])));
        }

        // no objective: any plan will do, and the search enumerates the plans
        // label the shore assignments first; the boat and moves follow from them
        BooleanVar[] decisions = new BooleanVar[4 * stages];
        for (int t = 0; t < stages; t++) {
            decisions[4 * t] = wolf[t];
            decisions[4 * t + 1] = goat[t];
            decisions[4 * t + 2] = cabbage[t];
            decisions[4 * t + 3] = boat[t];
        }
        Model model = new Model()
            .put("wolf_pos", wolf)
            .put("goat_pos", goat)
            .put("cabbage_pos", cabbage)
            .put("boat_pos", boat);
        return model.search(decisions, null, null);
    }
}
