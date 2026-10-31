// Balanced incomplete block design (CSPLib 028, BIBD) with parameters (v, b, r, k, l).
// matrix[i][j] = 1 if object i occurs in block j. The v x b incidence matrix must have:
//   - every row (object) with exactly r ones (each object is in r blocks),
//   - every column (block) with exactly k ones (each block holds k objects),
//   - every pair of distinct rows with a scalar product of exactly l (every two objects
//     occur together in l blocks).
// The dimensions and the parameters all come from the instance.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int v = inst.getInt("v");   // objects (rows of the incidence matrix)
        int b = inst.getInt("b");   // blocks (columns)
        int r = inst.getInt("r");   // blocks per object
        int k = inst.getInt("k");   // objects per block
        int l = inst.getInt("l");   // blocks shared by every pair of objects

        // matrix[i][j] = 1 if object i is in block j
        BooleanVar[][] matrix = new BooleanVar[v][b];
        for (int i = 0; i < v; i++) {
            for (int j = 0; j < b; j++) {
                matrix[i][j] = new BooleanVar(store, "m" + i + "_" + j);
            }
        }

        // each object occurs in exactly r blocks: the row sums equal r
        int[] onesB = new int[b];
        java.util.Arrays.fill(onesB, 1);
        for (int i = 0; i < v; i++) {
            store.impose(new LinearInt(matrix[i], onesB, "==", r));
        }

        // each block holds exactly k objects: the column sums equal k
        int[] onesV = new int[v];
        java.util.Arrays.fill(onesV, 1);
        for (int j = 0; j < b; j++) {
            IntVar[] column = new IntVar[v];
            for (int i = 0; i < v; i++) {
                column[i] = matrix[i][j];
            }
            store.impose(new LinearInt(column, onesV, "==", k));
        }

        // every two distinct objects share exactly l blocks: the scalar product of
        // their rows equals l. prod[j] = 1 if both objects are in block j.
        for (int p = 0; p < v; p++) {
            for (int q = p + 1; q < v; q++) {
                IntVar[] prod = new IntVar[b];
                for (int j = 0; j < b; j++) {
                    prod[j] = new IntVar(store, 0, 1);
                    store.impose(new XmulYeqZ(matrix[p][j], matrix[q][j], prod[j]));
                }
                store.impose(new LinearInt(prod, onesB, "==", l));
            }
        }

        return new Model().put("matrix", matrix);
    }
}
