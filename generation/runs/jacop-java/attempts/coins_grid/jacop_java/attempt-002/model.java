// Coins on a grid: place coins on an n x n board so that every row and every
// column holds exactly c coins (at most one coin per cell). Minimise the sum,
// over all cells holding a coin, of the squared horizontal distance of the cell
// from the main diagonal, (column - row)^2.
// x[i][j] = 1 when cell (row i, column j) holds a coin; z is the cost.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.search.IndomainMax;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
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

        // Each row holds exactly c coins.
        for (int i = 0; i < n; i++) {
            IntVar[] row = new IntVar[n];
            int[] ones = new int[n];
            for (int j = 0; j < n; j++) {
                row[j] = x[i][j];
                ones[j] = 1;
            }
            store.impose(new LinearInt(row, ones, "==", c));
        }

        // Each column holds exactly c coins.
        for (int j = 0; j < n; j++) {
            IntVar[] col = new IntVar[n];
            int[] ones = new int[n];
            for (int i = 0; i < n; i++) {
                col[i] = x[i][j];
                ones[i] = 1;
            }
            store.impose(new LinearInt(col, ones, "==", c));
        }

        // Cost z = sum of (j - i)^2 over the cells holding a coin. The largest
        // possible cost is c coins in each of n rows, each at most (n-1)^2 away
        // from the diagonal.
        int maxCost = n * c * (n - 1) * (n - 1);
        IntVar z = new IntVar(store, 0, maxCost);
        IntVar[] terms = new IntVar[n * n + 1];
        int[] weights = new int[n * n + 1];
        int k = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                terms[k] = x[i][j];
                weights[k] = (j - i) * (j - i);
                k++;
            }
        }
        // The last term is z itself with weight -1, so the sum equals z.
        terms[k] = z;
        weights[k] = -1;
        store.impose(new LinearInt(terms, weights, "==", 0));

        // Search order: the cells nearest the diagonal (cheapest) first, and in
        // each cell try a coin first. A greedy-looking first solution then bounds
        // the cost early, which the branch and bound needs to prove the optimum.
        // Cells are sorted by their cost weight, ties in row-major order.
        Integer[] cells = new Integer[n * n];
        for (int t = 0; t < n * n; t++) {
            cells[t] = t;
        }
        java.util.Arrays.sort(cells, (a, b) -> weights[a] - weights[b]);
        IntVar[] order = new IntVar[n * n];
        for (int t = 0; t < n * n; t++) {
            order[t] = x[cells[t] / n][cells[t] % n];
        }

        // Minimise the cost. The runner proves the optimum.
        return new Model().put("x", x).put("z", z)
                .search(order, null, new IndomainMax<IntVar>())
                .minimize(z);
    }
}
