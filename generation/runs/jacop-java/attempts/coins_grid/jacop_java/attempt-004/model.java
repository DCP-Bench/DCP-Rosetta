// Coins on a grid: place coins on an n x n board so that every row and every
// column holds exactly c coins (at most one coin per cell). Minimise the sum,
// over all cells holding a coin, of the squared horizontal distance of the cell
// from the main diagonal, (column - row)^2.
// x[i][j] = 1 when cell (row i, column j) holds a coin; z is the cost.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.search.IndomainMin;
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
        int[] weights = new int[n * n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                weights[i * n + j] = (j - i) * (j - i);
            }
        }

        // Cost per row: rowCost[i] is the cost of the coins in row i. Its bounds
        // are the cheapest and the dearest c cells of the row, so the row costs
        // give the solver a lower bound it can prune with before the global sum.
        IntVar[] rowCost = new IntVar[n];
        IntVar[] colCost = new IntVar[n];
        for (int i = 0; i < n; i++) {
            int[] rowW = new int[n];
            for (int j = 0; j < n; j++) {
                rowW[j] = (j - i) * (j - i);
            }
            java.util.Arrays.sort(rowW);
            int low = 0, high = 0;
            for (int t = 0; t < c; t++) {
                low += rowW[t];
                high += rowW[n - 1 - t];
            }
            rowCost[i] = new IntVar(store, low, high);
            IntVar[] terms = new IntVar[n + 1];
            int[] w = new int[n + 1];
            for (int j = 0; j < n; j++) {
                terms[j] = x[i][j];
                w[j] = (j - i) * (j - i);
            }
            terms[n] = rowCost[i];
            w[n] = -1;
            store.impose(new LinearInt(terms, w, "==", 0));
        }
        // Column costs, the same way, with the cells of each column.
        for (int j = 0; j < n; j++) {
            int[] colW = new int[n];
            for (int i = 0; i < n; i++) {
                colW[i] = (j - i) * (j - i);
            }
            java.util.Arrays.sort(colW);
            int low = 0, high = 0;
            for (int t = 0; t < c; t++) {
                low += colW[t];
                high += colW[n - 1 - t];
            }
            colCost[j] = new IntVar(store, low, high);
            IntVar[] terms = new IntVar[n + 1];
            int[] w = new int[n + 1];
            for (int i = 0; i < n; i++) {
                terms[i] = x[i][j];
                w[i] = (j - i) * (j - i);
            }
            terms[n] = colCost[j];
            w[n] = -1;
            store.impose(new LinearInt(terms, w, "==", 0));
        }
        // The total is the sum of the row costs, and also of the column costs.
        IntVar[] rowTerms = new IntVar[n + 1];
        int[] rowOnes = new int[n + 1];
        IntVar[] colTerms = new IntVar[n + 1];
        int[] colOnes = new int[n + 1];
        for (int i = 0; i < n; i++) {
            rowTerms[i] = rowCost[i];
            rowOnes[i] = 1;
            colTerms[i] = colCost[i];
            colOnes[i] = 1;
        }
        rowTerms[n] = z;
        rowOnes[n] = -1;
        colTerms[n] = z;
        colOnes[n] = -1;
        store.impose(new LinearInt(rowTerms, rowOnes, "==", 0));
        store.impose(new LinearInt(colTerms, colOnes, "==", 0));

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
                .search(order, null, new IndomainMin<IntVar>())
                .minimize(z);
    }
}
