// Futoshiki: fill an n x n grid with the digits 1..n so that every row and every column
// holds each digit once, the given digits are kept, and each inequality sign holds.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XltY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray values = inst.getJSONArray("values");   // 0 = empty cell, otherwise a given digit
        int n = values.length();                           // grid size, from the instance
        JSONArray lt = inst.getJSONArray("lt");            // rows: r1 c1 r2 c2 (1-based), cell1 < cell2

        // grid[i][j] = digit in row i+1, column j+1
        IntVar[][] grid = new IntVar[n][n];
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                grid[i][j] = new IntVar(store, "g" + i + "_" + j, 1, n);

        // Latin square: each row and each column holds the digits 1..n exactly once
        for (int i = 0; i < n; i++) {
            store.impose(new Alldifferent(grid[i]));
            IntVar[] column = new IntVar[n];
            for (int j = 0; j < n; j++)
                column[j] = grid[j][i];
            store.impose(new Alldifferent(column));
        }

        // Givens: a non-zero entry fixes that cell
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                int v = values.getJSONArray(i).getInt(j);
                if (v != 0)
                    store.impose(new XeqC(grid[i][j], v));
            }

        // Inequality clues: the first cell is less than the second cell
        for (int k = 0; k < lt.length(); k++) {
            JSONArray c = lt.getJSONArray(k);
            IntVar a = grid[c.getInt(0) - 1][c.getInt(1) - 1];
            IntVar b = grid[c.getInt(2) - 1][c.getInt(3) - 1];
            store.impose(new XltY(a, b));
        }

        return new Model().put("grid", grid);
    }
}
