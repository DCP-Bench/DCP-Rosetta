// Magic hexagon: place the numbers 1..19 on the 19 cells of a hexagon (letters A..S, rows
// of 3, 4, 5, 4, 3) so that each of the 15 lines (5 rows and 10 diagonals) sums to MAGIC_SUM.
// LD lists the cells in the order A, B, ..., S.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        // The number of cells and the magic sum come from the instance.
        int n = instance.getInt("NUM_CELLS");
        int magic = instance.getInt("MAGIC_SUM");

        // One variable per cell, in the order A, B, ..., S.
        IntVar[] cell = new IntVar[n];
        for (int i = 0; i < n; i++) {
            cell[i] = new IntVar(store, 1, n);
        }
        int A = 0, B = 1, C = 2, D = 3, E = 4, F = 5, G = 6, H = 7, I = 8, J = 9, K = 10, L = 11,
            M = 12, N = 13, O = 14, P = 15, Q = 16, R = 17, S = 18;

        // The numbers 1..19 each used once.
        store.impose(new Alldifferent(cell));

        // The 15 lines, each a list of cells: the five horizontal rows, then the ten diagonals
        // in the two diagonal directions.
        int[][] lines = {
            // rows
            {A, B, C},
            {D, E, F, G},
            {H, I, J, K, L},
            {M, N, O, P},
            {Q, R, S},
            // down-right diagonals
            {H, M, Q},
            {D, I, N, R},
            {A, E, J, O, S},
            {B, F, K, P},
            {C, G, L},
            // down-left diagonals
            {A, D, H},
            {B, E, I, M},
            {C, F, J, N, Q},
            {G, K, O, R},
            {L, P, S}
        };

        // Each line sums to the magic constant.
        for (int[] line : lines) {
            IntVar[] vars = new IntVar[line.length];
            int[] ones = new int[line.length];
            for (int k = 0; k < line.length; k++) {
                vars[k] = cell[line[k]];
                ones[k] = 1;
            }
            store.impose(new LinearInt(vars, ones, "==", magic));
        }

        Model m = new Model().put("LD", cell);
        return m;
    }
}
