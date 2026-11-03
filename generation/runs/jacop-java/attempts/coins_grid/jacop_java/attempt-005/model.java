// Coins on a grid: place coins on an n x n board so that every row and every
// column holds exactly c coins (at most one coin per cell). Minimise the sum,
// over all cells holding a coin, of the squared horizontal distance of the cell
// from the main diagonal, (column - row)^2.
// x[i][j] = 1 when cell (row i, column j) holds a coin; z is the cost.
//
// Model: one Table constraint per row and per column. Its scope is the n cells
// of the line plus a line-cost variable, and its tuples are every placement of
// exactly c coins in the line together with that placement's cost. This gives
// the exact-c count and the cost bound in one propagator. z equals both the sum
// of the row costs and the sum of the column costs.
import java.util.ArrayList;
import java.util.List;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.table.Table;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.search.IndomainMax;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    // All 0/1 patterns of length n with exactly c ones, each followed by its cost
    // sum of (j - pos)^2 over the cells holding a coin. pos is the row (or column)
    // index of the line.
    static int[][] tuples(int n, int c, int pos) {
        List<int[]> out = new ArrayList<>();
        for (int mask = 0; mask < (1 << n); mask++) {
            if (Integer.bitCount(mask) != c) continue;
            int[] t = new int[n + 1];
            int cost = 0;
            for (int j = 0; j < n; j++) {
                if ((mask >> j & 1) == 1) {
                    t[j] = 1;
                    cost += (j - pos) * (j - pos);
                }
            }
            t[n] = cost;
            out.add(t);
        }
        return out.toArray(new int[0][]);
    }

    public static Model build(JSONObject inst, Store store) {
        // The board size and the coins per row and column come from the instance.
        int n = inst.getInt("n");
        int c = inst.getInt("c");

        // One Boolean per cell; at most one coin per cell is the Boolean's own range.
        BooleanVar[][] x = new BooleanVar[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                x[i][j] = new BooleanVar(store, "x" + i + "_" + j);
            }
        }

        // Row and column costs. Each cost variable ranges over the cheapest to the
        // dearest placement of c coins in a line, read off the tuples.
        IntVar[] rowCost = new IntVar[n];
        IntVar[] colCost = new IntVar[n];
        int rowSumLow = 0, rowSumHigh = 0, colSumLow = 0, colSumHigh = 0;
        for (int p = 0; p < n; p++) {
            // Row p: cells x[p][0..n-1]; its tuples use the column index as distance.
            int[][] tup = tuples(n, c, p);
            int lo = Integer.MAX_VALUE, hi = Integer.MIN_VALUE;
            for (int[] t : tup) {
                lo = Math.min(lo, t[n]);
                hi = Math.max(hi, t[n]);
            }
            rowCost[p] = new IntVar(store, "rc" + p, lo, hi);
            colCost[p] = new IntVar(store, "cc" + p, lo, hi);
            rowSumLow += lo;
            rowSumHigh += hi;
            colSumLow += lo;
            colSumHigh += hi;

            IntVar[] rowScope = new IntVar[n + 1];
            IntVar[] colScope = new IntVar[n + 1];
            for (int k = 0; k < n; k++) {
                rowScope[k] = x[p][k];
                colScope[k] = x[k][p];
            }
            rowScope[n] = rowCost[p];
            colScope[n] = colCost[p];
            // Column p has the same cost pattern as row p, since (i - j)^2 is symmetric.
            store.impose(new Table(rowScope, tup));
            store.impose(new Table(colScope, tup));
        }

        // z is the total cost: it equals both the sum of the row costs and the sum of
        // the column costs. Its bounds are the larger of the two lower bounds.
        IntVar z = new IntVar(store, "z", Math.max(rowSumLow, colSumLow), Math.min(rowSumHigh, colSumHigh));
        IntVar[] rowTerms = new IntVar[n + 1];
        IntVar[] colTerms = new IntVar[n + 1];
        int[] w = new int[n + 1];
        for (int i = 0; i < n; i++) {
            rowTerms[i] = rowCost[i];
            colTerms[i] = colCost[i];
            w[i] = 1;
        }
        rowTerms[n] = z;
        colTerms[n] = z;
        w[n] = -1;
        store.impose(new LinearInt(rowTerms, w, "==", 0));
        store.impose(new LinearInt(colTerms, w, "==", 0));

        // Search: cells nearest the diagonal (cheapest) first, and in each cell try
        // a coin first (IndomainMax). A good first solution bounds the cost early,
        // which the branch and bound needs to prove the optimum.
        Integer[] cells = new Integer[n * n];
        for (int t = 0; t < n * n; t++) {
            cells[t] = t;
        }
        java.util.Arrays.sort(cells, (a, b) -> {
            int da = a / n - a % n, db = b / n - b % n;
            return da * da - db * db;
        });
        IntVar[] order = new IntVar[n * n];
        for (int t = 0; t < n * n; t++) {
            order[t] = x[cells[t] / n][cells[t] % n];
        }

        return new Model().put("x", x).put("z", z)
                .search(order, null, new IndomainMax<IntVar>())
                .minimize(z);
    }
}
