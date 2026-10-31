// Hidato: fill a grid so that the numbers 1..R*C each appear once, consecutive numbers touch
// (horizontally, vertically or diagonally), and the given clues stay where they are.
// 0 in the puzzle marks an empty cell.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.Element;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XplusCeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Grid size and clues come from the instance; every array below is sized from it.
        JSONArray puzzle = inst.getJSONArray("puzzle");
        int rows = puzzle.length();
        int cols = puzzle.getJSONArray(0).length();
        int cells = rows * cols;

        // x[r][c] = the number written in cell (r, c), from 1 to the cell count.
        IntVar[][] x = new IntVar[rows][cols];
        IntVar[] flat = new IntVar[cells];
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                x[r][c] = new IntVar(store, "x" + r + "_" + c, 1, cells);
                flat[r * cols + c] = x[r][c];
                int clue = puzzle.getJSONArray(r).getInt(c);
                if (clue > 0) {
                    // a given clue stays in its cell
                    store.impose(new XeqC(x[r][c], clue));
                }
            }
        }
        // every number is written exactly once
        store.impose(new Alldifferent(flat));

        // Position of each number. pos[v] is the cell (row-major, 0-based) that holds the number
        // v+1. It is the row and the column together: pos = row * cols + col.
        // The row and column are kept separately so that adjacency is a simple difference test.
        IntVar[] pos = new IntVar[cells];
        IntVar[] row = new IntVar[cells];
        IntVar[] col = new IntVar[cells];
        for (int v = 0; v < cells; v++) {
            pos[v] = new IntVar(store, "pos" + v, 0, cells - 1);
            row[v] = new IntVar(store, "row" + v, 0, rows - 1);
            col[v] = new IntVar(store, "col" + v, 0, cols - 1);
            // pos[v] = row[v] * cols + col[v]
            store.impose(new LinearInt(new IntVar[]{pos[v], row[v], col[v]},
                                       new int[]{1, -cols, -1}, "==", 0));
        }
        // each number occupies its own cell
        store.impose(new Alldifferent(pos));

        // Channel positions with the grid. For cell i, the number written there (x - 1, so 0-based)
        // indexes pos and returns i: pos[x_i - 1] = i. This ties the grid to the positions.
        for (int i = 0; i < cells; i++) {
            IntVar zeroBased = new IntVar(store, "zero" + i, 0, cells - 1);
            // zeroBased = x_i - 1
            store.impose(new XplusCeqZ(zeroBased, 1, flat[i]));
            store.impose(Element.choose(zeroBased, pos, new IntVar(store, "cell" + i, i, i), -1));
        }

        // Consecutive numbers touch: the cells of v+1 and v+2 are at most one step apart in
        // rows and in columns, which gives horizontal, vertical and diagonal neighbours.
        for (int v = 0; v + 1 < cells; v++) {
            // row[v+1] - row[v] within -1..1
            store.impose(new LinearInt(new IntVar[]{row[v + 1], row[v]}, new int[]{1, -1}, "<=", 1));
            store.impose(new LinearInt(new IntVar[]{row[v], row[v + 1]}, new int[]{1, -1}, "<=", 1));
            // col[v+1] - col[v] within -1..1
            store.impose(new LinearInt(new IntVar[]{col[v + 1], col[v]}, new int[]{1, -1}, "<=", 1));
            store.impose(new LinearInt(new IntVar[]{col[v], col[v + 1]}, new int[]{1, -1}, "<=", 1));
        }

        // Output: the solved grid. Labelling the cells first fixes the rest.
        Model m = new Model().put("x", x);
        return m.search(flat, null, null);
    }
}
