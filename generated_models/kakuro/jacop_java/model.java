// Kakuro: fill the white (blank) cells of an n x n grid with digits 1..9 so that
// each clue's cells sum to the clue and no digit repeats within one clue's cells.
// Black cells print as 0. The grid size, the white cells and the clues all come
// from the instance.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.SumInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        JSONArray blanks = inst.getJSONArray("blanks");
        JSONArray clues = inst.getJSONArray("problem");

        // x[i][j] is the cell in row i, column j (0-based). Every cell takes a digit 1..9
        // unless the instance lists it in "blanks" (1-based [row, column] pairs): those
        // are the blank cells of the grid, which are fixed to 0 in the output.
        IntVar[][] x = new IntVar[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                x[i][j] = new IntVar(store, "x" + i + "_" + j, 1, 9);
            }
        }
        for (int b = 0; b < blanks.length(); b++) {
            JSONArray cell = blanks.getJSONArray(b);
            int r = cell.getInt(0) - 1;
            int c = cell.getInt(1) - 1;
            x[r][c] = new IntVar(store, 0, 0);
        }

        // Each clue is an entry: its first number is the sum, and each later entry is a
        // 1-based [row, column] pair of a cell the sum runs over. The entries are ragged,
        // so each one is read by its own length.
        for (int e = 0; e < clues.length(); e++) {
            JSONArray clue = clues.getJSONArray(e);
            int sum = clue.getInt(0);
            int len = clue.length() - 1;
            IntVar[] cells = new IntVar[len];
            for (int k = 0; k < len; k++) {
                JSONArray cell = clue.getJSONArray(k + 1);
                cells[k] = x[cell.getInt(0) - 1][cell.getInt(1) - 1];
            }
            // The cells of this clue sum to the clue value.
            store.impose(new SumInt(cells, "==", new IntVar(store, sum, sum)));
            // No digit is repeated within one clue.
            store.impose(new Alldifferent(cells));
        }

        // Output x is the grid with 0 for black cells.
        return new Model().put("x", x);
    }
}
