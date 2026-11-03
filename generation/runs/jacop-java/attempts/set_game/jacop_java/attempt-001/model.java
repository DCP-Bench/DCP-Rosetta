// Set: find three cards that form a "set". For each of the four features, the three
// cards must show that feature either all the same or all different.
// winning_cards holds the 0-based indices of the three cards, in ascending order, so each
// set is reported once (the order of its three cards does not matter for being a set).
import java.util.ArrayList;
import java.util.List;
import org.jacop.constraints.*;
import org.jacop.constraints.table.Table;
import org.jacop.core.*;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // the deck comes from the instance: one row per card, one column per feature
        JSONArray cards = inst.getJSONArray("cards_data");
        int n = cards.length();
        int features = cards.getJSONArray(0).length();

        // the three winning cards, as 0-based indices into the deck, in ascending order
        IntVar[] win = new IntVar[3];
        for (int k = 0; k < 3; k++) {
            win[k] = new IntVar(store, "card" + k, 0, n - 1);
        }
        store.impose(new XltY(win[0], win[1]));
        store.impose(new XltY(win[1], win[2]));

        // a feature has three possibilities, numbered 1..3 in the data
        // allowed value triples: all three the same, or all three different
        List<int[]> allowed = new ArrayList<>();
        for (int x = 1; x <= 3; x++) {
            for (int y = 1; y <= 3; y++) {
                for (int z = 1; z <= 3; z++) {
                    boolean allSame = x == y && y == z;
                    boolean allDifferent = x != y && y != z && x != z;
                    if (allSame || allDifferent) {
                        allowed.add(new int[]{x, y, z});
                    }
                }
            }
        }
        int[][] tuples = allowed.toArray(new int[0][]);

        for (int f = 0; f < features; f++) {
            // the value of feature f on each card of the deck
            int[] column = new int[n];
            for (int c = 0; c < n; c++) {
                column[c] = cards.getJSONArray(c).getInt(f);
            }
            // the value of feature f on each winning card, looked up from the winning index
            IntVar[] value = new IntVar[3];
            for (int k = 0; k < 3; k++) {
                value[k] = new IntVar(store, "f" + f + "card" + k, 1, 3);
                // element index is 0-based (offset -1)
                store.impose(Element.choose(win[k], column, value[k], -1));
            }
            // the three values of this feature must be all the same or all different
            store.impose(new Table(value, tuples));
        }

        Model m = new Model().put("winning_cards", win);
        // label the winning card indices first; the feature values follow from them
        m.search(win, null, null);
        return m;
    }
}
