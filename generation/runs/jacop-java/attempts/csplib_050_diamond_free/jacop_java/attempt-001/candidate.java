// Diamond-free graphs with constrained degree sequences (CSPLib 050).
// Find a simple undirected graph on N vertices, given by its adjacency matrix,
// that is diamond-free and whose degree sequence meets the problem's conditions.
//
// Variables: matrix[i][j] is 1 when vertices i and j are adjacent. The matrix is
// symmetric, has no loops (diagonal fixed to 0), and deg[i] is the degree of i.
//
// Constraints, in the problem's own terms:
//   - simple graph: no loop edges; the matrix is symmetric;
//   - the degree of each vertex is the number of its neighbours, and is greater
//     than zero (no isolated vertices);
//   - each degree is a multiple of 3 (modulo 3 = 0): deg[i] = 3 * q[i];
//   - the sum of the degrees is a multiple of 12, i.e. |E| is a multiple of 6:
//     sum(deg) = 12 * k;
//   - degrees are listed in non-increasing order: deg[i] >= deg[i+1];
//   - diamond-free: for every four vertices the number of edges among them is at
//     most 4 (a diamond has at least five), i.e. the six pairs sum to <= 4.
//
// Sizes come from the instance: N vertices. Nothing here depends on the example.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XgteqY;
import org.jacop.constraints.XmulCeqZ;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("N");

        // Adjacency matrix. matrix[i][j] = matrix[j][i] (an edge between i and j).
        IntVar[][] matrix = new IntVar[n][n];
        for (int i = 0; i < n; i++) {
            matrix[i][i] = new BooleanVar(store);
            store.impose(new XeqC(matrix[i][i], 0));   // simple graph: no loops
        }
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                matrix[i][j] = new BooleanVar(store);
                matrix[j][i] = matrix[i][j];
            }
        }

        // Degree of each vertex: the number of its neighbours.
        // Positive, and a multiple of 3: deg[i] = 3 * q[i], q[i] >= 1.
        int maxDeg = n - 1;
        IntVar[] deg = new IntVar[n];
        for (int i = 0; i < n; i++) {
            deg[i] = new IntVar(store, 1, maxDeg);
            IntVar[] row = new IntVar[n + 1];
            int[] w = new int[n + 1];
            for (int j = 0; j < n; j++) {
                row[j] = matrix[i][j];
                w[j] = 1;
            }
            row[n] = deg[i];
            w[n] = -1;
            store.impose(new LinearInt(row, w, "==", 0));

            int maxQ = maxDeg / 3;
            IntVar q = new IntVar(store, 1, maxQ);
            store.impose(new XmulCeqZ(q, 3, deg[i]));
        }

        // The sum of the degrees is a multiple of 12 (|E| is a multiple of 6).
        IntVar total = new IntVar(store, 0, n * maxDeg);
        store.impose(new SumInt(deg, "==", total));
        IntVar k = new IntVar(store, 0, n * maxDeg / 12);
        store.impose(new XmulCeqZ(k, 12, total));

        // Degree sequence is listed in non-increasing order.
        for (int i = 0; i + 1 < n; i++) {
            store.impose(new XgteqY(deg[i], deg[i + 1]));
        }

        // Diamond-free: among any four vertices at most four edges.
        for (int a = 0; a < n; a++) {
            for (int b = a + 1; b < n; b++) {
                for (int c = b + 1; c < n; c++) {
                    for (int d = c + 1; d < n; d++) {
                        IntVar[] edges = {
                            matrix[a][b], matrix[a][c], matrix[a][d],
                            matrix[b][c], matrix[b][d], matrix[c][d]
                        };
                        int[] ones = {1, 1, 1, 1, 1, 1};
                        store.impose(new LinearInt(edges, ones, "<=", 4));
                    }
                }
            }
        }

        Model m = new Model().put("matrix", matrix);
        return m;
    }
}
