// Magic square: fill an n x n grid, n from the instance, with the integers 1..n*n, each once,
// so that every row, every column and both diagonals sum to n*(n*n+1)/2.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        int cells = n * n;
        // The magic constant: n*(n*n+1)/2.
        int target = n * (n * n + 1) / 2;

        // square[r][c] is the entry in row r, column c, a value from 1 to n*n.
        IntVar[][] square = new IntVar[n][n];
        IntVar[] all = new IntVar[cells];
        for (int r = 0; r < n; r++)
            for (int c = 0; c < n; c++) {
                square[r][c] = new IntVar(store, "s" + r + "_" + c, 1, cells);
                all[r * n + c] = square[r][c];
            }

        // Every cell holds a different value.
        store.impose(new Alldifferent(all));

        int[] ones = new int[n];
        java.util.Arrays.fill(ones, 1);

        // Each row sums to the magic constant.
        for (int r = 0; r < n; r++)
            store.impose(new LinearInt(square[r], ones, "==", target));

        // Each column sums to the magic constant.
        for (int c = 0; c < n; c++) {
            IntVar[] col = new IntVar[n];
            for (int r = 0; r < n; r++) col[r] = square[r][c];
            store.impose(new LinearInt(col, ones, "==", target));
        }

        // The main diagonal sums to the magic constant.
        IntVar[] diag = new IntVar[n], anti = new IntVar[n];
        for (int i = 0; i < n; i++) {
            diag[i] = square[i][i];
            anti[i] = square[i][n - 1 - i];
        }
        store.impose(new LinearInt(diag, ones, "==", target));
        // The anti-diagonal sums to the magic constant.
        store.impose(new LinearInt(anti, ones, "==", target));

        return new Model().put("square", square);
    }
}
