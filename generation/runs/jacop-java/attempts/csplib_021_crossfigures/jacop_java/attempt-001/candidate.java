// Crossfigure: fill the 9x9 grid with digits so that every across and down answer
// satisfies its clue. M[r][c] is the digit in row r, column c (0 on a blocked cell).
// The puzzle is fixed by the problem statement, so the grid and clues are written out here.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.constraints.table.Table;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Submission {
    // "_" is an empty cell to fill, "X" a blocked cell, a number a clue label.
    static final String[] GRID = {
        "1 2 _ 3 X 4 _ 5 6",
        "7 _ X 8 _ _ X 9 _",
        "_ X 10 _ X 11 12 X _",
        "13 14 _ _ X 15 _ 16 _",
        "X _ X X X X X _ X",
        "17 _ 18 19 X 20 21 _ 22",
        "_ X 23 _ X 24 _ X _",
        "25 26 X 27 _ _ X 28 _",
        "29 _ _ _ X 30 _ _ _"
    };

    public static Model build(JSONObject instance, Store store) {
        int rows = GRID.length;
        int cols = GRID[0].split(" ").length;
        String[][] tok = new String[rows][cols];
        for (int r = 0; r < rows; r++) {
            tok[r] = GRID[r].split(" ");
        }

        // Words are maximal runs of at least two open cells, across and down. A word is named
        // by the clue label on its first cell: A<label> for across, D<label> for down.
        Map<String, List<int[]>> words = new LinkedHashMap<>();
        boolean[][] leading = new boolean[rows][cols];
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (tok[r][c].equals("X")) {
                    continue;
                }
                if (c == 0 || tok[r][c - 1].equals("X")) {
                    List<int[]> cells = run(tok, r, c, 0, 1);
                    if (cells.size() >= 2) {
                        words.put("A" + tok[r][c], cells);
                        leading[r][c] = true;
                    }
                }
                if (r == 0 || tok[r - 1][c].equals("X")) {
                    List<int[]> cells = run(tok, r, c, 1, 0);
                    if (cells.size() >= 2) {
                        words.put("D" + tok[r][c], cells);
                        leading[r][c] = true;
                    }
                }
            }
        }

        // Digit per open cell. A cell that starts a word cannot be a leading zero.
        IntVar[][] M = new IntVar[rows][cols];
        List<IntVar> decisions = new ArrayList<>();
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (tok[r][c].equals("X")) {
                    M[r][c] = new IntVar(store, 0, 0);
                } else {
                    M[r][c] = new IntVar(store, leading[r][c] ? 1 : 0, 9);
                    decisions.add(M[r][c]);
                }
            }
        }

        // The value of each word is the number its digits spell (most significant digit first).
        Map<String, IntVar> W = new HashMap<>();
        for (Map.Entry<String, List<int[]>> e : words.entrySet()) {
            List<int[]> cells = e.getValue();
            int len = cells.size();
            IntVar value = new IntVar(store, pow10(len - 1), pow10(len) - 1);
            W.put(e.getKey(), value);
            IntVar[] vars = new IntVar[len + 1];
            int[] weights = new int[len + 1];
            for (int k = 0; k < len; k++) {
                int[] rc = cells.get(k);
                vars[k] = M[rc[0]][rc[1]];
                weights[k] = pow10(len - 1 - k);
            }
            vars[len] = value;
            weights[len] = -1;
            store.impose(new LinearInt(vars, weights, "==", 0));
        }

        // Clues in the problem's own words, with the answer relation they give.

        // Across 1: 27 across times two.
        lin(store, W, "A1", 1, "A27", -2, 0);
        // Across 4: 4 down plus seventy-one.
        lin(store, W, "A4", 1, "D4", -1, 71);
        // Across 7: 18 down plus four.
        lin(store, W, "A7", 1, "D18", -1, 4);
        // Across 8: 6 down divided by sixteen (exact division, so 6 down = 16 * across 8).
        lin(store, W, "D6", 1, "A8", -16, 0);
        // Across 9: 2 down minus eighteen.
        lin(store, W, "A9", 1, "D2", -1, -18);
        // Across 10: dozen in six gross, i.e. the number of dozens in 6 * 144 = 864, which is 72.
        lin(store, W, "A10", 1, null, 0, 72);
        // Across 11: 5 down minus seventy.
        lin(store, W, "A11", 1, "D5", -1, -70);
        // Across 13: 26 down times 23 across.
        store.impose(new XmulYeqZ(need(W, "D26"), need(W, "A23"), need(W, "A13")));
        // Across 15: 6 down minus 350.
        lin(store, W, "A15", 1, "D6", -1, -350);
        // Across 17: 25 across times 23 across.
        store.impose(new XmulYeqZ(need(W, "A25"), need(W, "A23"), need(W, "A17")));
        // Across 20: a square number.
        inSet(store, words, M, W, "A20", squares(4));
        // Across 23: a prime number.
        inSet(store, words, M, W, "A23", primes(2));
        // Across 24: a square number.
        inSet(store, words, M, W, "A24", squares(2));
        // Across 25: 20 across divided by seventeen (exact, so 20 across = 17 * across 25).
        lin(store, W, "A20", 1, "A25", -17, 0);
        // Across 27: 6 down divided by four (exact, so 6 down = 4 * across 27).
        lin(store, W, "D6", 1, "A27", -4, 0);
        // Across 28: four dozen = 48.
        lin(store, W, "A28", 1, null, 0, 48);
        // Across 29: seven gross = 7 * 144 = 1008.
        lin(store, W, "A29", 1, null, 0, 1008);
        // Across 30: 22 down plus 450.
        lin(store, W, "A30", 1, "D22", -1, 450);

        // Down 1: 1 across plus twenty-seven.
        lin(store, W, "D1", 1, "A1", -1, 27);
        // Down 2: five dozen = 60.
        lin(store, W, "D2", 1, null, 0, 60);
        // Down 3: 30 across plus 888.
        lin(store, W, "D3", 1, "A30", -1, 888);
        // Down 4: two times 17 across.
        lin(store, W, "D4", 1, "A17", -2, 0);
        // Down 5: 29 across divided by twelve (exact, so 29 across = 12 * down 5).
        lin(store, W, "A29", 1, "D5", -12, 0);
        // Down 6: 28 across times 23 across.
        store.impose(new XmulYeqZ(need(W, "A28"), need(W, "A23"), need(W, "D6")));
        // Down 10: 10 across plus four.
        lin(store, W, "D10", 1, "A10", -1, 4);
        // Down 12: three times 24 across.
        lin(store, W, "D12", 1, "A24", -3, 0);
        // Down 14: 13 across divided by sixteen (exact, so 13 across = 16 * down 14).
        lin(store, W, "A13", 1, "D14", -16, 0);
        // Down 16: 28 down times fifteen.
        lin(store, W, "D16", 1, "D28", -15, 0);
        // Down 17: 13 across minus 399.
        lin(store, W, "D17", 1, "A13", -1, -399);
        // Down 18: 29 across divided by eighteen (exact, so 29 across = 18 * down 18).
        lin(store, W, "A29", 1, "D18", -18, 0);
        // Down 19: 22 down minus ninety-four.
        lin(store, W, "D19", 1, "D22", -1, -94);
        // Down 20: 20 across minus nine.
        lin(store, W, "D20", 1, "A20", -1, -9);
        // Down 21: 25 across minus fifty-two.
        lin(store, W, "D21", 1, "A25", -1, -52);
        // Down 22: 20 down times six.
        lin(store, W, "D22", 1, "D20", -6, 0);
        // Down 26: five times 24 across.
        lin(store, W, "D26", 1, "A24", -5, 0);
        // Down 28: 21 down plus twenty-seven.
        lin(store, W, "D28", 1, "D21", -1, 27);

        // Search over the digits. Word values follow from them.
        Model m = new Model().put("M", M);
        m.search(decisions.toArray(new IntVar[0]), null, null);
        return m;
    }

    // Cells of the run starting at (r, c) and stepping by (dr, dc) while cells are open.
    static List<int[]> run(String[][] tok, int r, int c, int dr, int dc) {
        List<int[]> cells = new ArrayList<>();
        int rr = r, cc = c;
        while (rr < tok.length && cc < tok[0].length && !tok[rr][cc].equals("X")) {
            cells.add(new int[]{rr, cc});
            rr += dr;
            cc += dc;
        }
        return cells;
    }

    static IntVar need(Map<String, IntVar> W, String key) {
        IntVar v = W.get(key);
        if (v == null) {
            throw new IllegalStateException("no word " + key + " in the grid");
        }
        return v;
    }

    // a * x + b * y == c, where y may be null (then just a * x == c).
    static void lin(Store store, Map<String, IntVar> W, String x, int a, String y, int b, int c) {
        if (y == null) {
            store.impose(new LinearInt(new IntVar[]{need(W, x)}, new int[]{a}, "==", c));
        } else {
            store.impose(new LinearInt(new IntVar[]{need(W, x), need(W, y)}, new int[]{a, b}, "==", c));
        }
    }

    // The digits of the word must spell one of the values (a table over its cells).
    static void inSet(Store store, Map<String, List<int[]>> words, IntVar[][] M, Map<String, IntVar> W,
                      String key, List<Integer> values) {
        List<int[]> cells = words.get(key);
        if (cells == null) {
            throw new IllegalStateException("no word " + key + " in the grid");
        }
        int len = cells.size();
        List<int[]> tuples = new ArrayList<>();
        for (int v : values) {
            String s = Integer.toString(v);
            if (s.length() != len) {
                continue;
            }
            int[] digits = new int[len];
            for (int k = 0; k < len; k++) {
                digits[k] = s.charAt(k) - '0';
            }
            tuples.add(digits);
        }
        IntVar[] vars = new IntVar[len];
        for (int k = 0; k < len; k++) {
            int[] rc = cells.get(k);
            vars[k] = M[rc[0]][rc[1]];
        }
        store.impose(new Table(vars, tuples.toArray(new int[0][])));
    }

    static List<Integer> squares(int len) {
        List<Integer> out = new ArrayList<>();
        for (int s = 0; s * s < pow10(len); s++) {
            if (s * s >= pow10(len - 1)) {
                out.add(s * s);
            }
        }
        return out;
    }

    static List<Integer> primes(int len) {
        List<Integer> out = new ArrayList<>();
        for (int v = pow10(len - 1); v < pow10(len); v++) {
            boolean prime = v > 1;
            for (int d = 2; d * d <= v && prime; d++) {
                if (v % d == 0) {
                    prime = false;
                }
            }
            if (prime) {
                out.add(v);
            }
        }
        return out;
    }

    static int pow10(int e) {
        int p = 1;
        for (int i = 0; i < e; i++) {
            p *= 10;
        }
        return p;
    }
}
