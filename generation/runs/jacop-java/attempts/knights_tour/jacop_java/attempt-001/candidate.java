// Knight's tour on an n x n board (n = instance field "n").
// Output x[r][c] = move number (0..n*n-1) at which the knight visits square (r, c).
// Every square is visited exactly once; consecutive moves are knight moves.
// The tour is open: it does not have to return to its starting square.
//
// Encoding: x (move number per square) is the declared output. cellAt[k] is the square
// (as r*n+c) visited at move k, the inverse of x. Successive moves are linked through
// cellAt: (cellAt[k], cellAt[k+1]) must be a knight move, posted as a table of all knight-move pairs.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.Element;
import org.jacop.constraints.table.Table;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;
import java.util.ArrayList;
import java.util.List;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        int cells = n * n;

        // x[r][c]: move number of square (r, c), 0-based
        IntVar[][] x = new IntVar[n][n];
        IntVar[] flat = new IntVar[cells];
        for (int r = 0; r < n; r++) {
            for (int c = 0; c < n; c++) {
                x[r][c] = new IntVar(store, "x_" + r + "_" + c, 0, cells - 1);
                flat[r * n + c] = x[r][c];
            }
        }

        // cellAt[k]: square visited at move k, encoded as r*n + c
        IntVar[] cellAt = new IntVar[cells];
        for (int k = 0; k < cells; k++) {
            cellAt[k] = new IntVar(store, "cellAt_" + k, 0, cells - 1);
        }

        // every square gets a distinct move number, and every move visits a distinct square
        store.impose(new Alldifferent(flat));
        store.impose(new Alldifferent(cellAt));

        // cellAt is the inverse of x: the square of move x[s] is s
        for (int s = 0; s < cells; s++) {
            IntVar square = new IntVar(store, s, s);
            store.impose(Element.choose(flat[s], cellAt, square, -1));
        }

        // consecutive moves are a knight move apart: list all knight-move pairs of squares
        int[] dr = {1, 1, -1, -1, 2, 2, -2, -2};
        int[] dc = {2, -2, 2, -2, 1, -1, 1, -1};
        List<int[]> pairs = new ArrayList<>();
        for (int r = 0; r < n; r++) {
            for (int c = 0; c < n; c++) {
                for (int d = 0; d < dr.length; d++) {
                    int nr = r + dr[d];
                    int nc = c + dc[d];
                    if (nr >= 0 && nr < n && nc >= 0 && nc < n) {
                        pairs.add(new int[]{r * n + c, nr * n + nc});
                    }
                }
            }
        }
        int[][] moves = pairs.toArray(new int[0][]);
        for (int k = 0; k + 1 < cells; k++) {
            store.impose(new Table(new IntVar[]{cellAt[k], cellAt[k + 1]}, moves));
        }

        Model m = new Model().put("x", x);
        // label the path in move order, so each move is a neighbour of the previous one
        m.search(cellAt, null, null);
        return m;
    }
}
