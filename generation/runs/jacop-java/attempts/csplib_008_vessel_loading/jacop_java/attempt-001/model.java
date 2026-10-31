// Vessel loading (CSPLib 008), decision version: place every container on the
// rectangular deck without overlap, with containers parallel to the deck sides
// (no turning: width along x, length along y), and with the minimum separation
// between containers of two classes respected.
//
// Coordinates start at 0 along the deck width (x, left to right) and the deck
// length (y, top to bottom). A container occupies [left, right) in x and
// [top, bottom) in y, so right = left + width and bottom = top + length.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Instance data: deck_width (x) by deck_length (y), n_containers containers
        // with width[i] and length[i], classes[i] (1-based), and separation[a][b]
        // the minimum gap between a class a+1 and a class b+1 container.
        int deckW = inst.getInt("deck_width");
        int deckL = inst.getInt("deck_length");
        int n = inst.getInt("n_containers");
        JSONArray widthJson = inst.getJSONArray("width");
        JSONArray lengthJson = inst.getJSONArray("length");
        JSONArray classJson = inst.getJSONArray("classes");
        JSONArray sepJson = inst.getJSONArray("separation");

        int[] width = new int[n];
        int[] length = new int[n];
        int[] cls = new int[n];
        for (int i = 0; i < n; i++) {
            width[i] = widthJson.getInt(i);
            length[i] = lengthJson.getInt(i);
            cls[i] = classJson.getInt(i);
        }

        // Positions of each container's corners on the deck (the declared outputs).
        // right and bottom are tied to left and top by the container's size, and
        // the domains keep every container inside the deck.
        IntVar[] left = new IntVar[n];
        IntVar[] top = new IntVar[n];
        IntVar[] right = new IntVar[n];
        IntVar[] bottom = new IntVar[n];
        for (int i = 0; i < n; i++) {
            left[i] = new IntVar(store, "left_" + i, 0, deckW - width[i]);
            top[i] = new IntVar(store, "top_" + i, 0, deckL - length[i]);
            right[i] = new IntVar(store, "right_" + i, width[i], deckW);
            bottom[i] = new IntVar(store, "bottom_" + i, length[i], deckL);

            // right = left + width
            IntVar[] rEq = {right[i], left[i]};
            store.impose(new LinearInt(rEq, new int[]{1, -1}, "==", width[i]));
            // bottom = top + length
            IntVar[] bEq = {bottom[i], top[i]};
            store.impose(new LinearInt(bEq, new int[]{1, -1}, "==", length[i]));
        }

        // No overlap, plus separation: two containers i and j are fine when one lies
        // at least sep to the left of, right of, above or below the other, where sep
        // is the required separation for their two classes. sep 0 is plain non-overlap.
        // Each of the four positions is a reified literal, and at least one must hold.
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                int sep = sepJson.getJSONArray(cls[i] - 1).getInt(cls[j] - 1);

                BooleanVar iLeftOfJ = new BooleanVar(store, "iLeft_" + i + "_" + j);
                BooleanVar jLeftOfI = new BooleanVar(store, "jLeft_" + i + "_" + j);
                BooleanVar iAboveJ = new BooleanVar(store, "iAbove_" + i + "_" + j);
                BooleanVar jAboveI = new BooleanVar(store, "jAbove_" + i + "_" + j);

                // i ends at least sep before j starts horizontally: right_i + sep <= left_j
                IntVar[] c1 = {right[i], left[j]};
                store.impose(new Reified(new LinearInt(c1, new int[]{1, -1}, "<=", -sep), iLeftOfJ));
                // j ends at least sep before i starts horizontally: right_j + sep <= left_i
                IntVar[] c2 = {right[j], left[i]};
                store.impose(new Reified(new LinearInt(c2, new int[]{1, -1}, "<=", -sep), jLeftOfI));
                // i ends at least sep before j starts vertically: bottom_i + sep <= top_j
                IntVar[] c3 = {bottom[i], top[j]};
                store.impose(new Reified(new LinearInt(c3, new int[]{1, -1}, "<=", -sep), iAboveJ));
                // j ends at least sep before i starts vertically: bottom_j + sep <= top_i
                IntVar[] c4 = {bottom[j], top[i]};
                store.impose(new Reified(new LinearInt(c4, new int[]{1, -1}, "<=", -sep), jAboveI));

                IntVar[] apart = {iLeftOfJ, jLeftOfI, iAboveJ, jAboveI};
                int[] ones = {1, 1, 1, 1};
                store.impose(new LinearInt(apart, ones, ">=", 1));
            }
        }

        // Labels the positions, left before top; the rest follows.
        IntVar[] order = new IntVar[2 * n];
        for (int i = 0; i < n; i++) {
            order[i] = left[i];
            order[n + i] = top[i];
        }

        // Satisfaction problem: no objective.
        return new Model()
                .put("left", left)
                .put("right", right)
                .put("top", top)
                .put("bottom", bottom)
                .search(order, null, null);
    }
}
