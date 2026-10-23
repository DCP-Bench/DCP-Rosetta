// Three coins: coins start tails, heads, tails (init, where 1 is tails). In exactly num_moves moves, each
// flipping one coin, make all coins face the same way. steps[t][i] is coin i after t moves (true = tails).
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XeqY;
import org.jacop.constraints.XneqY;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        JSONArray init = instance.getJSONArray("init");
        int coins = init.length();
        int moves = instance.getInt("num_moves");

        // steps[t][i]: coin i after t moves, true = tails
        BooleanVar[][] steps = new BooleanVar[moves + 1][coins];
        for (int t = 0; t <= moves; t++) {
            for (int i = 0; i < coins; i++) {
                steps[t][i] = new BooleanVar(store, "step" + t + "coin" + (i + 1));
            }
        }

        // the first row is the starting position
        for (int i = 0; i < coins; i++) {
            store.impose(new XeqC(steps[0][i], init.getInt(i)));
        }

        // each move flips exactly one coin: the coins that differ from the previous row number exactly one
        for (int t = 1; t <= moves; t++) {
            BooleanVar[] flipped = new BooleanVar[coins];
            int[] ones = new int[coins];
            for (int i = 0; i < coins; i++) {
                flipped[i] = new BooleanVar(store, "flip" + t + "coin" + (i + 1));
                store.impose(new Reified(new XneqY(steps[t - 1][i], steps[t][i]), flipped[i]));
                ones[i] = 1;
            }
            store.impose(new LinearInt(flipped, ones, "==", 1));
        }

        // after the last move all coins face the same way: all heads or all tails
        for (int i = 1; i < coins; i++) {
            store.impose(new XeqY(steps[moves][0], steps[moves][i]));
        }

        Model model = new Model().put("steps", steps);
        return model;
    }
}
