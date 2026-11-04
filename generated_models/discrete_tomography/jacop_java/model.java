// Discrete tomography: find a 0/1 matrix whose row sums and column sums are the given numbers.
// The matrix has as many rows as row_sums has entries and as many columns as col_sums has entries;
// the brief's [11][12] is the example's size only, so the shape follows each instance.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray rowSums = inst.getJSONArray("row_sums");
        JSONArray colSums = inst.getJSONArray("col_sums");
        int rows = rowSums.length();
        int cols = colSums.length();

        // matrix[r][c] = 1 if the cell in row r, column c holds a one.
        IntVar[][] matrix = new IntVar[rows][cols];
        IntVar[] cells = new IntVar[rows * cols];
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                matrix[r][c] = new BooleanVar(store, "cell_" + r + "_" + c);
                cells[r * cols + c] = matrix[r][c];
            }
        }

        // Each row contains as many ones as its row sum (the vertical x-ray).
        for (int r = 0; r < rows; r++) {
            int[] ones = new int[cols];
            java.util.Arrays.fill(ones, 1);
            store.impose(new LinearInt(matrix[r], ones, "==", rowSums.getInt(r)));
        }

        // Each column contains as many ones as its column sum (the horizontal x-ray).
        for (int c = 0; c < cols; c++) {
            IntVar[] column = new IntVar[rows];
            for (int r = 0; r < rows; r++) {
                column[r] = matrix[r][c];
            }
            int[] ones = new int[rows];
            java.util.Arrays.fill(ones, 1);
            store.impose(new LinearInt(column, ones, "==", colSums.getInt(c)));
        }

        // Label the cells in reading order; a satisfying matrix is all the output needs.
        return new Model().put("matrix", matrix).search(cells, null, null);
    }
}
