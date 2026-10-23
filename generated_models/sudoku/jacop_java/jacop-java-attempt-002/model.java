// Sudoku: fill a 9x9 grid with the digits 1 to 9 so that every row, every column and every 3x3 box
// contains each digit exactly once. The instance field input_grid gives the puzzle: 0 marks an empty cell,
// any other value is a fixed clue that the solution must keep.
// Output grid[r][c] = the digit in row r, column c of the solved grid.
// Each "all different" group is written as pairwise inequalities. Alldistinct (attempt-001) gave a second
// solution that broke the sudoku rules when the runner enumerated past the first one.
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XneqY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray given = inst.getJSONArray("input_grid");

        // grid[r][c]: the digit in row r, column c
        IntVar[][] grid = new IntVar[9][9];
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                grid[r][c] = new IntVar(store, "cell_" + r + "_" + c, 1, 9);
            }
        }

        // clues: every filled cell of the input keeps its digit
        for (int r = 0; r < 9; r++) {
            JSONArray row = given.getJSONArray(r);
            for (int c = 0; c < 9; c++) {
                int digit = row.getInt(c);
                if (digit != 0) {
                    store.impose(new XeqC(grid[r][c], digit));
                }
            }
        }

        // each row holds the digits 1 to 9 once each
        for (int r = 0; r < 9; r++) {
            IntVar[] row = new IntVar[9];
            for (int c = 0; c < 9; c++) {
                row[c] = grid[r][c];
            }
            allDifferent(store, row);
        }

        // each column holds the digits 1 to 9 once each
        for (int c = 0; c < 9; c++) {
            IntVar[] column = new IntVar[9];
            for (int r = 0; r < 9; r++) {
                column[r] = grid[r][c];
            }
            allDifferent(store, column);
        }

        // each 3x3 box holds the digits 1 to 9 once each
        for (int br = 0; br < 3; br++) {
            for (int bc = 0; bc < 3; bc++) {
                IntVar[] box = new IntVar[9];
                int k = 0;
                for (int r = 0; r < 3; r++) {
                    for (int c = 0; c < 3; c++) {
                        box[k++] = grid[3 * br + r][3 * bc + c];
                    }
                }
                allDifferent(store, box);
            }
        }

        return new Model().put("grid", grid);
    }

    // every pair of the group differs
    private static void allDifferent(Store store, IntVar[] vars) {
        for (int i = 0; i < vars.length; i++) {
            for (int j = i + 1; j < vars.length; j++) {
                store.impose(new XneqY(vars[i], vars[j]));
            }
        }
    }
}
