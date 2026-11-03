// Heterosquare of order n: an n x n square of distinct integers 1..n^2 whose
// row sums, column sums and two diagonal sums are all different from each other.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XneqY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // The order n comes from the instance; every size below follows it.
        int n = inst.getInt("n");
        int cells = n * n;
        // A line sums n cells, each at most n*n, so no sum can exceed n^3.
        int maxSum = n * cells;

        // x[i][j] is the cell in row i, column j; values are the integers 1..n^2.
        IntVar[][] x = new IntVar[n][n];
        IntVar[] flat = new IntVar[cells];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                x[i][j] = new IntVar(store, "x" + i + "_" + j, 1, cells);
                flat[i * n + j] = x[i][j];
            }
        }
        // The elements of the square are distinct.
        store.impose(new Alldifferent(flat));

        // The sums of the 2n+2 lines (n rows, n columns, 2 diagonals) are tied to
        // variables, so that they can be compared pairwise.
        IntVar[] sums = new IntVar[2 * n + 2];
        for (int i = 0; i < n; i++) {
            IntVar[] row = new IntVar[n];
            IntVar[] col = new IntVar[n];
            for (int j = 0; j < n; j++) {
                row[j] = x[i][j];
                col[j] = x[j][i];
            }
            // sums[i] is the sum of row i.
            sums[i] = new IntVar(store, "row" + i, 1, maxSum);
            store.impose(new SumInt(row, "==", sums[i]));
            // sums[n+i] is the sum of column i.
            sums[n + i] = new IntVar(store, "col" + i, 1, maxSum);
            store.impose(new SumInt(col, "==", sums[n + i]));
        }
        // sums[2n] is the main diagonal (top left to bottom right).
        IntVar[] diag = new IntVar[n];
        // sums[2n+1] is the anti-diagonal (top right to bottom left).
        IntVar[] anti = new IntVar[n];
        for (int i = 0; i < n; i++) {
            diag[i] = x[i][i];
            anti[i] = x[i][n - 1 - i];
        }
        sums[2 * n] = new IntVar(store, "diag", 1, maxSum);
        store.impose(new SumInt(diag, "==", sums[2 * n]));
        sums[2 * n + 1] = new IntVar(store, "anti", 1, maxSum);
        store.impose(new SumInt(anti, "==", sums[2 * n + 1]));

        // The 2n+2 line sums are pairwise different.
        for (int a = 0; a < sums.length; a++) {
            for (int b = a + 1; b < sums.length; b++) {
                store.impose(new XneqY(sums[a], sums[b]));
            }
        }

        // Output x is the square. Label the cells first.
        return new Model().put("x", x).search(flat, null, null);
    }
}
