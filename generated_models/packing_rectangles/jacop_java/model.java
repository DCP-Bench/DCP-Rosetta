// Rectangle packing: place each rectangle (widths[i] x heights[i], not rotated) at a position with its
// corner at (pos_x[i], pos_y[i]), so that no two rectangles overlap and all lie inside a container of
// width total_x and height total_y. Minimise the container area total_x * total_y.
import org.jacop.constraints.*;
import org.jacop.constraints.cumulative.Cumulative;
import org.jacop.core.*;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray widthJson = inst.getJSONArray("widths");
        JSONArray heightJson = inst.getJSONArray("heights");
        int n = widthJson.length();
        int[] w = new int[n];
        int[] h = new int[n];
        int sumW = 0;
        int sumH = 0;
        for (int i = 0; i < n; i++) {
            w[i] = widthJson.getInt(i);
            h[i] = heightJson.getInt(i);
            sumW += w[i];
            sumH += h[i];
        }

        // The container is at most as wide as all the rectangles side by side, and as tall as all stacked.
        IntVar totalX = new IntVar(store, 0, sumW);
        IntVar totalY = new IntVar(store, 0, sumH);

        // Corner positions: a rectangle must fit inside the container, so pos_x[i] + w[i] <= total_x.
        IntVar[] posX = new IntVar[n];
        IntVar[] posY = new IntVar[n];
        for (int i = 0; i < n; i++) {
            posX[i] = new IntVar(store, "posX" + i, 0, sumW - w[i]);
            posY[i] = new IntVar(store, "posY" + i, 0, sumH - h[i]);
            store.impose(new XplusClteqZ(posX[i], w[i], totalX));
            store.impose(new XplusClteqZ(posY[i], h[i], totalY));
        }

        // No overlap: each rectangle is the box {x, y, width, height}, and Diff2 keeps every pair of boxes apart.
        IntVar[][] rects = new IntVar[n][4];
        for (int i = 0; i < n; i++) {
            rects[i][0] = posX[i];
            rects[i][1] = posY[i];
            rects[i][2] = new IntVar(store, w[i], w[i]);
            rects[i][3] = new IntVar(store, h[i], h[i]);
        }
        store.impose(new Diff2(rects));

        // Redundant constraints, implied by the packing, that make propagation much stronger:
        // every rectangle fits in the container on its own, and the rectangles cross any vertical line
        // with at most total_y of height (x-direction cumulative), and any horizontal line with at most
        // total_x of width (y-direction cumulative).
        IntVar[] durationX = new IntVar[n];
        IntVar[] heightRes = new IntVar[n];
        IntVar[] durationY = new IntVar[n];
        IntVar[] widthRes = new IntVar[n];
        for (int i = 0; i < n; i++) {
            durationX[i] = new IntVar(store, w[i], w[i]);
            heightRes[i] = new IntVar(store, h[i], h[i]);
            durationY[i] = new IntVar(store, h[i], h[i]);
            widthRes[i] = new IntVar(store, w[i], w[i]);
        }
        store.impose(new Cumulative(posX, durationX, heightRes, totalY));
        store.impose(new Cumulative(posY, durationY, widthRes, totalX));

        int maxW = 0, maxH = 0, sumArea = 0;
        for (int i = 0; i < n; i++) {
            maxW = Math.max(maxW, w[i]);
            maxH = Math.max(maxH, h[i]);
            sumArea += w[i] * h[i];
        }
        store.impose(new XgteqC(totalX, maxW));
        store.impose(new XgteqC(totalY, maxH));

        // Objective: the container area, total_x * total_y. The area is at least the rectangles' total area.
        IntVar area = new IntVar(store, sumArea, sumW * sumH);
        store.impose(new XmulYeqZ(totalX, totalY, area));

        // Search over the positions first, then the container size.
        IntVar[] order = new IntVar[2 * n + 2];
        for (int i = 0; i < n; i++) {
            order[i] = posX[i];
            order[n + i] = posY[i];
        }
        order[2 * n] = totalX;
        order[2 * n + 1] = totalY;

        Model m = new Model().put("pos_x", posX).put("pos_y", posY).put("total_x", totalX).put("total_y", totalY);
        m.search(order, null, null);
        return m.minimize(area);
    }
}
