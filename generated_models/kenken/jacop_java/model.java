// KenKen: fill an n x n grid with the digits 1..n so that every row and every column
// holds each digit once, and each cage (a group of cells with a target number) reaches
// its target by one of the operations. The instance gives no operation per cage, so a
// cage is satisfied when its cells sum to the target, or multiply to it, or, for a
// two-cell cage, differ by it or divide into it.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Grid size and cages come from the instance.
        int n = inst.getInt("n");
        JSONArray cages = inst.getJSONArray("problem");

        // x[i][j] is the digit in row i, column j (0-based), a digit 1..n.
        IntVar[][] x = new IntVar[n][n];
        IntVar[] flat = new IntVar[n * n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                x[i][j] = new IntVar(store, "x" + i + "_" + j, 1, n);
                flat[i * n + j] = x[i][j];
            }
        }

        // Each row and each column contains each digit exactly once.
        for (int i = 0; i < n; i++) {
            IntVar[] row = new IntVar[n];
            IntVar[] col = new IntVar[n];
            for (int j = 0; j < n; j++) {
                row[j] = x[i][j];
                col[j] = x[j][i];
            }
            store.impose(new Alldifferent(row));
            store.impose(new Alldifferent(col));
        }

        // Each cage: an entry [target, [[row, column], ...]] with 1-based cells.
        for (int e = 0; e < cages.length(); e++) {
            JSONArray cage = cages.getJSONArray(e);
            int target = cage.getInt(0);
            JSONArray cellList = cage.getJSONArray(1);
            int m = cellList.length();
            IntVar[] cells = new IntVar[m];
            for (int k = 0; k < m; k++) {
                JSONArray cell = cellList.getJSONArray(k);
                cells[k] = x[cell.getInt(0) - 1][cell.getInt(1) - 1];
            }

            // The cage is satisfied when at least one of its options holds. Each option
            // gets a Boolean that is 1 exactly when that option holds. A two-cell cage has
            // six options: sum, product, difference (both orders) and quotient (both orders).
            int optionCount = (m == 2) ? 6 : 2;
            BooleanVar[] options = new BooleanVar[optionCount];
            int[] ones = new int[optionCount];
            java.util.Arrays.fill(ones, 1);

            // Addition: the cells sum to the target.
            IntVar sum = new IntVar(store, m, m * n);
            store.impose(new SumInt(cells, "==", sum));
            options[0] = new BooleanVar(store, "sum" + e);
            store.impose(new Reified(new XeqC(sum, target), options[0]));

            // Multiplication: the cells multiply to the target. The running product is
            // kept in a chain of variables, one per extra cell.
            IntVar prod = cells[0];
            for (int k = 1; k < m; k++) {
                int hi = 1;
                for (int t = 0; t <= k; t++) {
                    hi *= n;
                }
                IntVar next = new IntVar(store, 1, hi);
                store.impose(new XmulYeqZ(prod, cells[k], next));
                prod = next;
            }
            options[1] = new BooleanVar(store, "prod" + e);
            store.impose(new Reified(new XeqC(prod, target), options[1]));

            if (m == 2) {
                IntVar a = cells[0];
                IntVar b = cells[1];
                // Subtraction: the difference of the two cells is the target, in either order.
                options[2] = new BooleanVar(store, "diffAB" + e);
                store.impose(new Reified(
                    new LinearInt(new IntVar[]{a, b}, new int[]{1, -1}, "==", target), options[2]));
                options[3] = new BooleanVar(store, "diffBA" + e);
                store.impose(new Reified(
                    new LinearInt(new IntVar[]{a, b}, new int[]{-1, 1}, "==", target), options[3]));
                // Division: one cell is the target times the other, in either order.
                options[4] = new BooleanVar(store, "quotAB" + e);
                store.impose(new Reified(
                    new LinearInt(new IntVar[]{a, b}, new int[]{1, -target}, "==", 0), options[4]));
                options[5] = new BooleanVar(store, "quotBA" + e);
                store.impose(new Reified(
                    new LinearInt(new IntVar[]{a, b}, new int[]{-target, 1}, "==", 0), options[5]));
            }

            // At least one option holds.
            store.impose(new LinearInt(options, ones, ">=", 1));
        }

        // Output x is the solved grid. Label the cells first.
        return new Model().put("x", x).search(flat, null, null);
    }
}
