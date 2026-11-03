// Vessel loading (CSPLib 008), decision version. Each container is placed on the deck_width x
// deck_length deck and may be turned by 90 degrees: right-left is its width or its length (and
// top-bottom the other one). Coordinates start at 0; right/top are the exclusive far edges, so
// top = bottom + vertical extent (top is the larger y). Containers must not overlap, and a pair
// of classes (a, b) needs a gap of separation[a-1][b-1] in x or in y.
// Model: one 0/1 variable per placement (container, orientation, left, bottom), exactly one per
// container, channelled to left/bottom/turned. Every deck cell is covered by at most one placement
// (exactly one when the container areas fill the deck), which is the non-overlap constraint and
// propagates far better than pairwise disjunctions. Separation gaps are added as pairwise
// disjunctions only for class pairs that need one.
// Search: the placement variables in bottom-left order (anchor row, column, container, orientation),
// value max, which fills the lowest free cell first. Labelling the placements is needed: with
// only left/bottom/turned labelled the first solution overlapped (see lessons.md).
import org.jacop.constraints.*;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int W = inst.getInt("deck_width");
        int L = inst.getInt("deck_length");
        int n = inst.getInt("n_containers");
        JSONArray wj = inst.getJSONArray("width"), lj = inst.getJSONArray("length");
        JSONArray cj = inst.getJSONArray("classes"), sj = inst.getJSONArray("separation");
        int[] w = new int[n], l = new int[n], cls = new int[n];
        for (int i = 0; i < n; i++) {
            w[i] = wj.getInt(i); l[i] = lj.getInt(i); cls[i] = cj.getInt(i);
        }

        IntVar[] left = new IntVar[n], right = new IntVar[n], top = new IntVar[n], bottom = new IntVar[n];
        IntVar[] ex = new IntVar[n], ey = new IntVar[n], turned = new IntVar[n];
        for (int i = 0; i < n; i++) {
            left[i] = new IntVar(store, "left_" + i, 0, W);
            right[i] = new IntVar(store, "right_" + i, 0, W);
            bottom[i] = new IntVar(store, "bottom_" + i, 0, L);
            top[i] = new IntVar(store, "top_" + i, 0, L);
            turned[i] = (w[i] == l[i]) ? new IntVar(store, 0, 0) : new BooleanVar(store, "turned_" + i);
            ex[i] = new IntVar(store, "ex_" + i, Math.min(w[i], l[i]), Math.max(w[i], l[i]));
            ey[i] = new IntVar(store, "ey_" + i, Math.min(w[i], l[i]), Math.max(w[i], l[i]));
            // right - left = w + (l - w) * turned ; top - bottom = l + (w - l) * turned
            store.impose(new LinearInt(new IntVar[]{right[i], left[i], turned[i]}, new int[]{1, -1, -(l[i] - w[i])}, "==", w[i]));
            store.impose(new LinearInt(new IntVar[]{top[i], bottom[i], turned[i]}, new int[]{1, -1, -(w[i] - l[i])}, "==", l[i]));
            store.impose(new XplusYeqZ(left[i], ex[i], right[i]));
            store.impose(new XplusYeqZ(bottom[i], ey[i], top[i]));
        }

        // pairwise separation (only where a gap is needed; sep 0 is covered by the cell constraints)
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++) {
                int sep = sj.getJSONArray(cls[i] - 1).getInt(cls[j] - 1);
                if (sep == 0) continue;
                IntVar[] b = new IntVar[4];
                IntVar[][] pr = {{right[i], left[j]}, {right[j], left[i]}, {top[i], bottom[j]}, {top[j], bottom[i]}};
                for (int k = 0; k < 4; k++) {
                    b[k] = new BooleanVar(store, "sep" + i + "_" + j + "_" + k);
                    store.impose(new Reified(new LinearInt(pr[k], new int[]{1, -1}, "<=", -sep), b[k]));
                }
                store.impose(new LinearInt(b, new int[]{1, 1, 1, 1}, ">=", 1));
            }

        // placement booleans: one per (container, orientation, x, y); exactly one per container.
        // Cell coverage: every deck cell is covered by at most one container (exactly one when the
        // container areas fill the deck). This implies non-overlap and propagates much more strongly.
        long totalArea = 0;
        for (int i = 0; i < n; i++) totalArea += (long) w[i] * l[i];
        boolean exact = totalArea == (long) W * L;
        java.util.Map<IntVar,int[]> key = new java.util.HashMap<>();
        java.util.List<IntVar> allp = new java.util.ArrayList<>();
        java.util.List<IntVar>[] cell = new java.util.List[W * L];
        for (int c = 0; c < W * L; c++) cell[c] = new java.util.ArrayList<>();
        for (int i = 0; i < n; i++) {
            java.util.List<IntVar> pv = new java.util.ArrayList<>(), tv = new java.util.ArrayList<>();
            java.util.List<Integer> px = new java.util.ArrayList<>(), py = new java.util.ArrayList<>();
            for (int o = 0; o < (w[i] == l[i] ? 1 : 2); o++) {
                int ew = o == 0 ? w[i] : l[i], eh = o == 0 ? l[i] : w[i];
                for (int x = 0; x + ew <= W; x++)
                    for (int y = 0; y + eh <= L; y++) {
                        BooleanVar p = new BooleanVar(store, "p" + i + "_" + o + "_" + x + "_" + y);
                        allp.add(p); key.put(p, new int[]{y, x, i, o}); pv.add(p); px.add(x); py.add(y);
                        if (o == 1) tv.add(p);
                        for (int cx = x; cx < x + ew; cx++)
                            for (int cy = y; cy < y + eh; cy++) cell[cx * L + cy].add(p);
                    }
            }
            IntVar[] pa = pv.toArray(new IntVar[0]);
            int m = pa.length;
            store.impose(new LinearInt(pa, ones(m), "==", 1));
            // left = sum x*p, bottom = sum y*p, turned = sum of the turned placements
            IntVar[] lv = java.util.Arrays.copyOf(pa, m + 1), bv = java.util.Arrays.copyOf(pa, m + 1), tt = new IntVar[tv.size() + 1];
            int[] lw = new int[m + 1], bw = new int[m + 1], tw = new int[tv.size() + 1];
            for (int k = 0; k < m; k++) { lw[k] = px.get(k); bw[k] = py.get(k); }
            lv[m] = left[i]; lw[m] = -1; bv[m] = bottom[i]; bw[m] = -1;
            store.impose(new LinearInt(lv, lw, "==", 0));
            store.impose(new LinearInt(bv, bw, "==", 0));
            for (int k = 0; k < tv.size(); k++) { tt[k] = tv.get(k); tw[k] = 1; }
            tt[tv.size()] = turned[i]; tw[tv.size()] = -1;
            store.impose(new LinearInt(tt, tw, "==", 0));
        }
        for (int c = 0; c < W * L; c++) {
            if (cell[c].isEmpty()) continue;
            IntVar[] cv = cell[c].toArray(new IntVar[0]);
            store.impose(new LinearInt(cv, ones(cv.length), exact ? "==" : "<=", 1));
        }

        // bottom-left filling order: by anchor cell (y, then x), then container, then orientation;
        // with value max, the first free cell either gets a container anchored there or none
        allp.sort((a, b) -> java.util.Arrays.compare(key.get(a), key.get(b)));
        IntVar[] order = allp.toArray(new IntVar[0]);
        return new Model().put("left", left).put("right", right).put("top", top).put("bottom", bottom)
                .search(order, null, new org.jacop.search.IndomainMax<IntVar>());
    }

    static int[] ones(int m) { int[] a = new int[m]; java.util.Arrays.fill(a, 1); return a; }
}
