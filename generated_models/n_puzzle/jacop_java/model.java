// N-puzzle (sliding tiles): find a sequence of N_STEPS board states from the start board to the end board.
// Each step moves the blank (0) to one of its four neighbours, swapping it with the tile there.
// Output steps[t][r][c] is the tile at row r, column c after step t; steps[0] is the start, the last is the end.
import org.jacop.constraints.*;
import org.jacop.constraints.table.Table;
import org.jacop.core.*;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int stepCount = inst.getInt("N_STEPS");
        JSONArray startJson = inst.getJSONArray("puzzle_start");
        JSONArray endJson = inst.getJSONArray("puzzle_end");
        int n = startJson.length();
        int cells = n * n;

        // tile[t][k]: the tile on cell k after step t, where cell k = row * n + column and 0 is the blank.
        IntVar[][] tile = new IntVar[stepCount][cells];
        for (int t = 0; t < stepCount; t++) {
            for (int k = 0; k < cells; k++) {
                tile[t][k] = new IntVar(store, "tile" + t + "_" + k, 0, cells - 1);
            }
        }
        // blank[t]: the cell holding the blank after step t.
        IntVar[] blank = new IntVar[stepCount];
        for (int t = 0; t < stepCount; t++) {
            blank[t] = new IntVar(store, "blank" + t, 0, cells - 1);
        }

        // Each board state uses every tile exactly once.
        for (int t = 0; t < stepCount; t++) {
            store.impose(new Alldifferent(tile[t]));
        }

        // The blank is on cell k exactly when cell k holds tile 0.
        for (int t = 0; t < stepCount; t++) {
            for (int k = 0; k < cells; k++) {
                BooleanVar isBlank = new BooleanVar(store, "isBlank" + t + "_" + k);
                store.impose(new Reified(new XeqC(tile[t][k], 0), isBlank));
                store.impose(new Reified(new XeqC(blank[t], k), isBlank));
            }
        }

        // The start and end boards from the instance.
        for (int r = 0; r < n; r++) {
            for (int c = 0; c < n; c++) {
                int k = r * n + c;
                store.impose(new XeqC(tile[0][k], startJson.getJSONArray(r).getInt(c)));
                store.impose(new XeqC(tile[stepCount - 1][k], endJson.getJSONArray(r).getInt(c)));
            }
        }

        // One move per step: the blank goes from cell p to a neighbour q, and the tile on q slides into p.
        // For each cell k after the move, src is the cell whose tile ends up on k:
        //   k = p (the blank left k):      src = q, the tile that slid in;
        //   k = q (the blank arrived at k): src = p, the blank itself (tile 0), so k becomes 0;
        //   otherwise:                     src = k, the tile does not move.
        // The Table lists these triples for each adjacent (p, q) pair, which also forces the blank to move
        // to a neighbour. Element then copies tile[t][src] onto cell k.
        for (int t = 0; t + 1 < stepCount; t++) {
            for (int k = 0; k < cells; k++) {
                IntVar src = new IntVar(store, "src" + t + "_" + k, 0, cells - 1);
                store.impose(new Table(new IntVar[]{blank[t], blank[t + 1], src}, moveTuples(n, k)));
                store.impose(Element.choose(src, tile[t], tile[t + 1][k], -1));
            }
        }

        // Output as steps[t][row][column].
        IntVar[][][] steps = new IntVar[stepCount][n][n];
        for (int t = 0; t < stepCount; t++) {
            for (int r = 0; r < n; r++) {
                for (int c = 0; c < n; c++) {
                    steps[t][r][c] = tile[t][r * n + c];
                }
            }
        }

        Model m = new Model().put("steps", steps);
        // Search over the blank's position at each step: fixing all of them fixes every board.
        m.search(blank, null, null);
        return m;
    }

    // All triples (blank before, blank after, src) for a move of the blank between adjacent cells, for cell k.
    private static int[][] moveTuples(int n, int k) {
        List<int[]> tuples = new ArrayList<>();
        for (int p = 0; p < n * n; p++) {
            int pr = p / n, pc = p % n;
            int[][] dirs = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
            for (int[] d : dirs) {
                int qr = pr + d[0], qc = pc + d[1];
                if (qr < 0 || qr >= n || qc < 0 || qc >= n) continue;
                int q = qr * n + qc;
                int src = (p == k) ? q : (q == k) ? p : k;
                tuples.add(new int[]{p, q, src});
            }
        }
        return tuples.toArray(new int[0][]);
    }
}
