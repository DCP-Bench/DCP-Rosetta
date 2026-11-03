// Flip rows and columns: an R x C matrix of integers (input_matrix in the instance). Choose a sign -1 or 1
// for every row and every column so that every row sum and every column sum of the flipped matrix is
// non-negative, and the total sum of the flipped matrix is as small as possible.
// Cell (i, j) is flipped exactly when its row or its column is flipped, but not both, so its sign is
// rowSign[i] * colSign[j]. With flip booleans f[i] (row) and g[j] (column), the cell sign is -1 exactly
// when y[i][j] = (f[i] != g[j]) holds, so the flipped value is v - 2 v y and every sum is linear in y.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XneqY;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray input = inst.getJSONArray("input_matrix");
        int rows = input.length();
        int cols = input.getJSONArray(0).length();

        int[][] v = new int[rows][cols];
        int[] rowSum = new int[rows];
        int[] colSum = new int[cols];
        int absTotal = 0;
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                v[i][j] = input.getJSONArray(i).getInt(j);
                rowSum[i] += v[i][j];
                colSum[j] += v[i][j];
                absTotal += Math.abs(v[i][j]);
            }
        }
        int plainTotal = 0;
        for (int i = 0; i < rows; i++) {
            plainTotal += rowSum[i];
        }

        // f[i] = 1 if row i is flipped; g[j] = 1 if column j is flipped.
        // rowSign[i] = 1 - 2 f[i] and colSign[j] = 1 - 2 g[j], so the output is -1 or 1.
        BooleanVar[] f = new BooleanVar[rows];
        BooleanVar[] g = new BooleanVar[cols];
        IntVar[] rowSign = new IntVar[rows];
        IntVar[] colSign = new IntVar[cols];
        for (int i = 0; i < rows; i++) {
            f[i] = new BooleanVar(store, "flip_row_" + i);
            rowSign[i] = new IntVar(store, "row_sign_" + i, -1, 1);
            store.impose(new LinearInt(new IntVar[]{rowSign[i], f[i]}, new int[]{1, 2}, "==", 1));
        }
        for (int j = 0; j < cols; j++) {
            g[j] = new BooleanVar(store, "flip_col_" + j);
            colSign[j] = new IntVar(store, "col_sign_" + j, -1, 1);
            store.impose(new LinearInt(new IntVar[]{colSign[j], g[j]}, new int[]{1, 2}, "==", 1));
        }

        // y[i][j] = 1 when cell (i, j) changes sign: exactly one of its row and column is flipped.
        BooleanVar[][] y = new BooleanVar[rows][cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                y[i][j] = new BooleanVar(store, "changed_" + i + "_" + j);
                store.impose(new Reified(new XneqY(f[i], g[j]), y[i][j]));
            }
        }

        // Every row sum after flipping is >= 0: sum_j (v - 2 v y) >= 0.
        for (int i = 0; i < rows; i++) {
            IntVar[] vars = new IntVar[cols];
            int[] weights = new int[cols];
            for (int j = 0; j < cols; j++) {
                vars[j] = y[i][j];
                weights[j] = -2 * v[i][j];
            }
            store.impose(new LinearInt(vars, weights, ">=", -rowSum[i]));
        }

        // Every column sum after flipping is >= 0.
        for (int j = 0; j < cols; j++) {
            IntVar[] vars = new IntVar[rows];
            int[] weights = new int[rows];
            for (int i = 0; i < rows; i++) {
                vars[i] = y[i][j];
                weights[i] = -2 * v[i][j];
            }
            store.impose(new LinearInt(vars, weights, ">=", -colSum[j]));
        }

        // The overall sum after flipping: total = plainTotal - 2 * sum v y.
        // Written as sum(-2 v y) - total = -plainTotal so that total is a variable of the model.
        int cells = rows * cols;
        IntVar[] allVars = new IntVar[cells + 1];
        int[] allWeights = new int[cells + 1];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                allVars[i * cols + j] = y[i][j];
                allWeights[i * cols + j] = -2 * v[i][j];
            }
        }
        IntVar total = new IntVar(store, "total", -absTotal, absTotal);
        allVars[cells] = total;
        allWeights[cells] = -1;
        store.impose(new LinearInt(allVars, allWeights, "==", -plainTotal));

        // Label the column flips first (few of them), then the row flips; each row's flip is then
        // nearly forced by its sum constraint, and the cell flags and the total follow from them.
        IntVar[] decisions = new IntVar[rows + cols];
        for (int j = 0; j < cols; j++) {
            decisions[j] = g[j];
        }
        for (int i = 0; i < rows; i++) {
            decisions[cols + i] = f[i];
        }

        return new Model()
                .put("row_signs", rowSign)
                .put("col_signs", colSign)
                .minimize(total)
                .search(decisions, null, null);
    }
}
