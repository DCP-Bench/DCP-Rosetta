// Grocery puzzle: a kid buys num_items items. Adding the prices gives total_price
// cents; multiplying them (as dollar amounts, i.e. product in cents divided by
// 100^(num_items-1)) gives the same total. Find the item prices in cents.
//
// Product reading: prices are in cents and multiplied as dollar amounts, so
// product(prices) = total_price * 100^(num_items-1) in cents. (The brief does not
// state this scale; the dataset notes for the instances say "sum and product (in cents)".)
//
// JaCoP limit: IntDomain.MaxInt is 536870909, below the full product. So the
// items are split in two halves, each half multiplied separately (small), and a
// Table over (first half, second half) lists the pairs whose product is the target.
import org.jacop.constraints.*;
import org.jacop.constraints.table.Table;
import org.jacop.core.*;
import org.json.JSONObject;
import java.util.*;
import dcp.jacop.Model;

public class Submission {
    static final long CAP = 500_000_000L; // stay below IntDomain.MaxInt

    public static Model build(JSONObject inst, Store store) {
        int total = inst.getInt("total_price");
        int n = inst.getInt("num_items");
        long target = total;
        for (int i = 1; i < n; i++) target *= 100;

        // Each price divides the product target and is at most the total (prices are positive).
        IntervalDomain divs = new IntervalDomain();
        for (int d = 1; d <= total; d++) if (target % d == 0) divs.unionAdapt(d, d);
        IntVar[] p = new IntVar[n];
        for (int i = 0; i < n; i++) p[i] = new IntVar(store, "p" + i, divs.clone());

        // The prices add up to the total.
        int[] w = new int[n];
        Arrays.fill(w, 1);
        store.impose(new LinearInt(p, w, "==", total));

        // The prices (in dollars) multiply to the total: split in two halves joined by a Table.
        if (n >= 2) {
            int k = n / 2;
            IntVar a = chain(store, p, 0, k, total);
            IntVar b = chain(store, p, k, n, total);
            List<int[]> rows = new ArrayList<>();
            for (long x = 1; x <= Math.min(a.max(), target); x++) {
                if (target % x == 0 && target / x <= b.max()) rows.add(new int[]{(int) x, (int) (target / x)});
            }
            store.impose(new Table(new IntVar[]{a, b}, rows.toArray(new int[0][])));
        }
        // Prices are interchangeable: list them in non-decreasing order (symmetry breaking).
        for (int i = 0; i + 1 < n; i++) store.impose(new XlteqY(p[i], p[i + 1]));
        return new Model().put("prices", p).search(p, null, null);
    }

    // Product of p[from..to) as a variable, capped below JaCoP's maximum domain value.
    static IntVar chain(Store store, IntVar[] p, int from, int to, int total) {
        IntVar acc = p[from];
        long bound = total;
        for (int i = from + 1; i < to; i++) {
            bound = Math.min(bound * total, CAP);
            IntVar nx = new IntVar(store, "h" + i, 1, (int) bound);
            store.impose(new XmulYeqZ(acc, p[i], nx));
            acc = nx;
        }
        return acc;
    }
}
