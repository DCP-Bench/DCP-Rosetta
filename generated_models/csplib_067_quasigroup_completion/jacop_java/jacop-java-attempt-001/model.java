// Quasigroup completion (CSPLib 067): complete a partially filled order-N Latin square.
// Every cell holds a symbol from 1..N, each symbol occurs once in every row and every
// column, and the given cells (non-zero entries of "start") keep their values.
// Output puzzle: the completed N x N square.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.XeqC;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("N");              // order of the quasigroup
        JSONArray start = inst.getJSONArray("start");   // 0 marks an empty cell

        IntVar[][] puzzle = new IntVar[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                // Each cell holds a symbol 1..N.
                puzzle[i][j] = new IntVar(store, "q" + i + "_" + j, 1, n);
            }
        }

        // The given cells keep their value.
        for (int i = 0; i < n; i++) {
            JSONArray row = start.getJSONArray(i);
            for (int j = 0; j < n; j++) {
                int given = row.getInt(j);
                if (given != 0) {
                    store.impose(new XeqC(puzzle[i][j], given));
                }
            }
        }

        // Latin square: each row has all different symbols.
        for (int i = 0; i < n; i++) {
            store.impose(new Alldifferent(puzzle[i]));
        }
        // Latin square: each column has all different symbols.
        for (int j = 0; j < n; j++) {
            IntVar[] column = new IntVar[n];
            for (int i = 0; i < n; i++) {
                column[i] = puzzle[i][j];
            }
            store.impose(new Alldifferent(column));
        }

        Model m = new Model().put("puzzle", puzzle);
        m.search(flatten(puzzle), null, null); // label every cell, row by row
        return m;
    }

    private static IntVar[] flatten(IntVar[][] grid) {
        int n = grid.length;
        IntVar[] flat = new IntVar[n * n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                flat[i * n + j] = grid[i][j];
            }
        }
        return flat;
    }
}
