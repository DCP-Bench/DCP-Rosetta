// Crossword: fill the 6x5 grid below by choosing 8 of the 15 given words, one per numbered slot,
// so that all crossing letters agree.
// Output E[k] is the index of the word starting at clue number k+1 (reading order), where the
// words are numbered 0..14 sorted by length (longest first), then alphabetically.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.table.Table;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;
import java.util.ArrayList;
import java.util.List;

public class Submission {

    // Problem constants from the statement, not from the instance. '#' is a black cell.
    static final String[] GRID = {
        ".....",
        "##.#.",
        "#....",
        ".#...",
        ".....",
        ".##.#",
    };

    // The 15 words, sorted by length (longest first), then alphabetically.
    static final String[] WORDS = {
        "HOSES", "LASER", "SAILS", "SHEET", "STEER",   // length 5
        "HEEL", "HIKE", "KEEL", "KNOT", "LINE",        // length 4
        "AFT", "ALE", "EEL", "LEE", "TIE",             // length 3
    };

    static boolean open(int r, int c) {
        return r >= 0 && r < GRID.length && c >= 0 && c < GRID[0].length() && GRID[r].charAt(c) == '.';
    }

    public static Model build(JSONObject instance, Store store) {
        int rows = GRID.length, cols = GRID[0].length();

        // One letter variable per open cell, coded 0..25 for A..Z.
        IntVar[][] letter = new IntVar[rows][cols];
        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (open(r, c)) letter[r][c] = new IntVar(store, "L" + r + "_" + c, 0, 25);

        // Slots: each run of two or more open cells that starts at a cell, read in reading order.
        // Across before down at the same cell. Each slot gets the next clue number.
        List<List<int[]>> slots = new ArrayList<>();
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (!open(r, c)) continue;
                if (!open(r, c - 1) && open(r, c + 1)) {          // across word starts here
                    List<int[]> cells = new ArrayList<>();
                    for (int cc = c; open(r, cc); cc++) cells.add(new int[]{r, cc});
                    slots.add(cells);
                }
                if (!open(r - 1, c) && open(r + 1, c)) {          // down word starts here
                    List<int[]> cells = new ArrayList<>();
                    for (int rr = r; open(rr, c); rr++) cells.add(new int[]{rr, c});
                    slots.add(cells);
                }
            }
        }

        // E[k]: which word fills slot k. Its letters must match the cells it covers.
        IntVar[] E = new IntVar[slots.size()];
        for (int k = 0; k < slots.size(); k++) {
            List<int[]> cells = slots.get(k);
            int len = cells.size();
            IntVar w = new IntVar(store, "E" + k, 0, WORDS.length - 1);
            E[k] = w;

            // Table over (word index, letter of each cell). Only words of this slot's length fit.
            IntVar[] vars = new IntVar[len + 1];
            vars[0] = w;
            for (int i = 0; i < len; i++) vars[i + 1] = letter[cells.get(i)[0]][cells.get(i)[1]];

            List<int[]> tuples = new ArrayList<>();
            for (int j = 0; j < WORDS.length; j++) {
                if (WORDS[j].length() != len) continue;
                int[] t = new int[len + 1];
                t[0] = j;
                for (int i = 0; i < len; i++) t[i + 1] = WORDS[j].charAt(i) - 'A';
                tuples.add(t);
            }
            store.impose(new Table(vars, tuples.toArray(new int[0][])));
        }

        // Select 8 different words.
        store.impose(new Alldifferent(E));

        return new Model().put("E", E);
    }
}
