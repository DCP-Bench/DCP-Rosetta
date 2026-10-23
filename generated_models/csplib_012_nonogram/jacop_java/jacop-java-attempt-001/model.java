// Nonogram: shade cells of a rows x cols grid so that every row and every column
// reads, from left to right (top to bottom), as its list of consecutive shaded blocks.
// board[i][j] = 1 when cell (i, j) is shaded, 0 otherwise.
//
// Encoding: each line (one row or one column) is a deterministic automaton over its
// cells. The state after each cell is a variable, and a Table constraint on the triple
// (state before, cell, state after) allows only the transitions the automaton has.
import org.jacop.constraints.table.Table;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

import java.util.ArrayList;
import java.util.List;

public class Submission {

    public static Model build(JSONObject inst, Store store) {
        // Sizes and clues come from the instance. Clues are padded with leading zeros
        // (for example [0, 0, 3, 1]); zeros are not blocks and are dropped.
        int rows = inst.getInt("rows");
        int cols = inst.getInt("cols");
        JSONArray rowRules = inst.getJSONArray("row_rules");
        JSONArray colRules = inst.getJSONArray("col_rules");

        // Each cell is 0 (empty) or 1 (shaded).
        IntVar[][] board = new IntVar[rows][cols];
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                board[i][j] = new IntVar(store, "board_" + i + "_" + j, 0, 1);

        // Row constraints: the shaded runs of row i, read left to right, are the row's clue.
        for (int i = 0; i < rows; i++) {
            IntVar[] line = new IntVar[cols];
            for (int j = 0; j < cols; j++) line[j] = board[i][j];
            postLine(store, line, blocksOf(rowRules.getJSONArray(i)), "row " + i);
        }

        // Column constraints: the shaded runs of column j, read top to bottom, are the column's clue.
        for (int j = 0; j < cols; j++) {
            IntVar[] line = new IntVar[rows];
            for (int i = 0; i < rows; i++) line[i] = board[i][j];
            postLine(store, line, blocksOf(colRules.getJSONArray(j)), "col " + j);
        }

        return new Model().put("board", board);
    }

    // The non-zero entries of a clue, in order.
    static int[] blocksOf(JSONArray clue) {
        List<Integer> blocks = new ArrayList<>();
        for (int k = 0; k < clue.length(); k++) {
            int v = clue.getInt(k);
            if (v > 0) blocks.add(v);
        }
        int[] out = new int[blocks.size()];
        for (int k = 0; k < out.length; k++) out[k] = blocks.get(k);
        return out;
    }

    // Post "the 0/1 cells of this line form exactly the blocks, in order, with at least one
    // empty cell between consecutive blocks". The automaton has these states:
    //   A(k)      k blocks are finished and the last cell is empty (or nothing is read yet).
    //             Id k, for k = 0..m, where m = number of blocks.
    //   In(k, p)  block k is in progress, with p of its cells shaded so far (1 <= p <= blocks[k]).
    //             Id offset[k] + p - 1.
    // Accepting: A(m), i.e. the line ends with an empty cell after the last block; and
    // In(m-1, blocks[m-1]), i.e. the last block runs to the final cell.
    static void postLine(Store store, IntVar[] cells, int[] blocks, String name) {
        int len = cells.length;
        int m = blocks.length;

        int[] offset = new int[m];
        int next = m + 1;
        for (int k = 0; k < m; k++) {
            offset[k] = next;
            next += blocks[k];
        }
        int states = next;

        // q[j] is the state after reading the first j cells; q[0] is the start state A(0).
        IntVar[] q = new IntVar[len + 1];
        q[0] = new IntVar(store, name + " state 0", 0, 0);
        for (int j = 1; j <= len; j++)
            q[j] = new IntVar(store, name + " state " + j, 0, states - 1);

        for (int j = 0; j < len; j++) {
            List<int[]> tuples = new ArrayList<>();
            for (int s = 0; s < states; s++) {
                for (int bit = 0; bit <= 1; bit++) {
                    int t = step(s, bit, blocks, offset);
                    if (t < 0) continue;
                    // The last cell must leave the automaton in an accepting state.
                    if (j == len - 1 && !accepting(t, m, states)) continue;
                    tuples.add(new int[]{s, bit, t});
                }
            }
            store.impose(new Table(new IntVar[]{q[j], cells[j], q[j + 1]},
                                   tuples.toArray(new int[0][])));
        }
    }

    // Transition of the automaton on one cell (bit = 0 empty, 1 shaded). Returns -1 when
    // the cell is not allowed in that state.
    static int step(int s, int bit, int[] blocks, int[] offset) {
        int m = blocks.length;
        if (s <= m) {
            // A(k): an empty cell keeps waiting; a shaded cell starts block k, if one is left.
            int k = s;
            if (bit == 0) return k;
            return k < m ? offset[k] : -1;
        }
        // In(k, p): find the block that state s belongs to.
        int k = 0;
        while (k + 1 < m && offset[k + 1] <= s) k++;
        int p = s - offset[k] + 1;
        if (bit == 1) return p < blocks[k] ? s + 1 : -1;   // extend block k
        return p == blocks[k] ? k + 1 : -1;                // close block k with an empty cell
    }

    static boolean accepting(int s, int m, int states) {
        return s == m || (m > 0 && s == states - 1);
    }
}
