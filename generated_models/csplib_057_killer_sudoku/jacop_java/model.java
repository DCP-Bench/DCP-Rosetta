// Killer sudoku: fill an n x n grid (n = 9 in the example) with digits 1..n so that
// every row, every column and every nonet (box x box sub-grid, box = sqrt(n)) holds each digit once,
// and every cage (a sum and a set of cells) has cells summing to its total with no digit repeated.
// Cage cells in the instance are 1-based (row, column); the grid array is 0-based.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        int box = (int) Math.round(Math.sqrt(n)); // side of a nonet, derived from the grid size

        // Output x[r][c]: the digit in row r, column c (0-based here, reported as a grid).
        IntVar[][] x = new IntVar[n][n];
        IntVar[] cells = new IntVar[n * n];
        for (int r = 0; r < n; r++) {
            for (int c = 0; c < n; c++) {
                x[r][c] = new IntVar(store, "x_" + r + "_" + c, 1, n);
                cells[r * n + c] = x[r][c];
            }
        }

        // Each row contains each digit exactly once.
        for (int r = 0; r < n; r++) {
            store.impose(new Alldifferent(x[r]));
        }

        // Each column contains each digit exactly once.
        for (int c = 0; c < n; c++) {
            IntVar[] col = new IntVar[n];
            for (int r = 0; r < n; r++) {
                col[r] = x[r][c];
            }
            store.impose(new Alldifferent(col));
        }

        // Each nonet (box x box block) contains each digit exactly once.
        for (int br = 0; br < n; br += box) {
            for (int bc = 0; bc < n; bc += box) {
                IntVar[] nonet = new IntVar[n];
                int k = 0;
                for (int r = br; r < br + box; r++) {
                    for (int c = bc; c < bc + box; c++) {
                        nonet[k++] = x[r][c];
                    }
                }
                store.impose(new Alldifferent(nonet));
            }
        }

        // Cages: the instance lists [sum, [[row, col], ...]] per cage, 1-based coordinates.
        JSONArray cages = inst.getJSONArray("problem");
        for (int i = 0; i < cages.length(); i++) {
            JSONArray cage = cages.getJSONArray(i);
            int total = cage.getInt(0);
            JSONArray coords = cage.getJSONArray(1);
            IntVar[] vars = new IntVar[coords.length()];
            int[] ones = new int[coords.length()];
            for (int j = 0; j < coords.length(); j++) {
                JSONArray rc = coords.getJSONArray(j);
                vars[j] = x[rc.getInt(0) - 1][rc.getInt(1) - 1];
                ones[j] = 1;
            }
            // No digit repeated inside a cage (the standard killer sudoku rule).
            store.impose(new Alldifferent(vars));
            // The digits of the cage sum to the cage total.
            store.impose(new LinearInt(vars, ones, "==", total));
        }

        // Label the grid cells first; they are the only variables that decide the output.
        return new Model().put("x", x).search(cells, null, null);
    }
}
