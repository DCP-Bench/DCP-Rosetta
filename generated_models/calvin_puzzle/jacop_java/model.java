// Calvin puzzle: fill an n by n grid with the numbers 1..n*n, each once, so that each number
// k+1 is placed relative to number k by one of two moves:
//   Type I  (horizontal or vertical): exactly three squares away, i.e. a row or column
//           difference of 3 with the other difference 0;
//   Type II (diagonal): exactly two squares away, i.e. a row and a column difference of 2.
// x[i][j] is the number in row i, column j (0-based).
import java.util.ArrayList;
import java.util.List;
import org.jacop.constraints.*;
import org.jacop.constraints.table.Table;
import org.jacop.core.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // the grid size comes from the instance
        int n = inst.getInt("n");
        int cells = n * n;

        // cell[p] is the number in the cell with index p = row * n + col
        IntVar[] cell = new IntVar[cells];
        for (int p = 0; p < cells; p++) {
            cell[p] = new IntVar(store, "cell" + p, 1, cells);
        }
        store.impose(new Alldifferent(cell));

        // pos[k-1] is the cell index holding number k
        IntVar[] pos = new IntVar[cells];
        for (int k = 1; k <= cells; k++) {
            pos[k - 1] = new IntVar(store, "pos" + k, 0, cells - 1);
            // the cell at pos[k-1] holds the number k
            IntVar number = new IntVar(store, k, k);
            store.impose(Element.choose(pos[k - 1], cell, number, -1));
        }

        // allowed cell pairs (p, q) for consecutive numbers: p holds k, q holds k+1
        List<int[]> moves = new ArrayList<>();
        for (int p = 0; p < cells; p++) {
            for (int q = 0; q < cells; q++) {
                int dr = q / n - p / n;
                int dc = q % n - p % n;
                boolean typeI = (dr == 0 && Math.abs(dc) == 3) || (Math.abs(dr) == 3 && dc == 0);
                boolean typeII = Math.abs(dr) == 2 && Math.abs(dc) == 2;
                if (typeI || typeII) {
                    moves.add(new int[]{p, q});
                }
            }
        }
        int[][] allowed = moves.toArray(new int[0][]);
        for (int k = 0; k < cells - 1; k++) {
            store.impose(new Table(new IntVar[]{pos[k], pos[k + 1]}, allowed));
        }

        // output grid: x[i][j] is cell i * n + j
        IntVar[][] x = new IntVar[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                x[i][j] = cell[i * n + j];
            }
        }

        Model m = new Model().put("x", x);
        // label the positions of the numbers in order; the grid follows from them
        m.search(pos, null, null);
        return m;
    }
}
