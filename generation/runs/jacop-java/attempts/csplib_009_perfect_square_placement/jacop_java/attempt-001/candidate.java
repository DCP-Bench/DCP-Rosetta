// Perfect square placement (CSPLib 009, squared square): pack squares of the
// given integer sides into one bigger square of side `base` without overlap,
// with borders parallel to the big square's borders and no spare capacity.
//
// Variables: x[i], y[i] are the lower-left corner of square i, counted from 0.
// The domains keep each square inside the big square: 0 <= x[i] <= base - side[i].
//
// Constraints, in the problem's own terms:
//   - no two squares overlap: Diff2 over the rectangles (x, y, side, side);
//   - no spare capacity is implied by the instances: the squares' areas sum to
//     base * base, so non-overlap inside the base square fills it exactly.
//
// Sizes come from the instance: `base` and the list `sides`. The number of
// squares is the length of `sides`, so the output shapes follow each instance.
// The problem's "simple" condition (no sub-rectangle formed by a subset of the
// squares) is not posted: the description states it only as a definition.

import org.jacop.constraints.Diff2;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int base = inst.getInt("base");
        JSONArray sidesJson = inst.getJSONArray("sides");
        int n = sidesJson.length();

        IntVar[] x = new IntVar[n];
        IntVar[] y = new IntVar[n];
        IntVar[][] rects = new IntVar[n][4];

        for (int i = 0; i < n; i++) {
            int side = sidesJson.getInt(i);
            x[i] = new IntVar(store, "x_" + i, 0, base - side);
            y[i] = new IntVar(store, "y_" + i, 0, base - side);
            // A square is a rectangle whose width and height are both its side.
            IntVar w = new IntVar(store, side, side);
            IntVar h = new IntVar(store, side, side);
            rects[i] = new IntVar[]{x[i], y[i], w, h};
        }

        // No two squares overlap in the big square.
        store.impose(new Diff2(rects));

        Model m = new Model().put("x_coords", x).put("y_coords", y);
        return m;
    }
}
