// Solitaire battleships (CSPLib 014): fill a rows x cols grid so that every cell is
// water, a submarine (one-cell ship), or one part of a horizontal or vertical ship
// (left end, right end, top end, bottom end, or middle). The fleet is given as
// fleet_counts: how many ships of each length. Ships do not touch, not even
// diagonally. The row and column sums give how many cells in each row and column
// are occupied by a vessel. Hints fix some cells to a given code.
//
// Cell codes come from the instance: WATER, CIRCLE (submarine), LEFT, RIGHT, TOP,
// BOTTOM, MIDDLE. The code _SHIP is never a final cell value and is excluded.

import java.util.ArrayList;
import java.util.List;

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.table.Table;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Instance data: grid size, row and column sums, fleet, hints (row, col, code).
        int rows = inst.getInt("rows");
        int cols = inst.getInt("cols");
        JSONArray rowSum = inst.getJSONArray("rowsum");
        JSONArray colSum = inst.getJSONArray("colsum");
        JSONArray fleet = inst.getJSONArray("fleet_counts");
        JSONArray hints = inst.getJSONArray("hints");

        int water = inst.getInt("WATER");
        int circle = inst.getInt("CIRCLE");
        int left = inst.getInt("LEFT");
        int right = inst.getInt("RIGHT");
        int top = inst.getInt("TOP");
        int bottom = inst.getInt("BOTTOM");
        int middle = inst.getInt("MIDDLE");

        // Cell values allowed in the final grid: water and the six ship codes.
        int[] codes = {water, circle, left, right, top, bottom, middle};
        int maxCode = 0;
        for (int code : codes) {
            maxCode = Math.max(maxCode, code);
        }

        // cell[r][c] = the code of the cell (the declared output).
        IntVar[][] cell = new IntVar[rows][cols];
        List<IntVar> flat = new ArrayList<>();
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                cell[r][c] = new IntVar(store, "cell_" + r + "_" + c, 0, maxCode);
                flat.add(cell[r][c]);
            }
        }

        // Local shape rule. For every cell, the codes of its four orthogonal neighbours
        // (up, left, right, down) must fit the cell's own code. Outside the grid counts as water.
        // Tuples are enumerated over the codes, so a cell can never take an unlisted value.
        List<int[]> shapeTuples = new ArrayList<>();
        for (int u : codes) {
            for (int l : codes) {
                for (int s : codes) {
                    for (int rt : codes) {
                        for (int d : codes) {
                            if (shapeValid(u, l, s, rt, d, water, circle, left, right, top, bottom, middle)) {
                                shapeTuples.add(new int[]{u, l, s, rt, d});
                            }
                        }
                    }
                }
            }
        }
        int[][] shapeTable = shapeTuples.toArray(new int[0][]);
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                IntVar up = r > 0 ? cell[r - 1][c] : new IntVar(store, water, water);
                IntVar lf = c > 0 ? cell[r][c - 1] : new IntVar(store, water, water);
                IntVar rt = c < cols - 1 ? cell[r][c + 1] : new IntVar(store, water, water);
                IntVar dn = r < rows - 1 ? cell[r + 1][c] : new IntVar(store, water, water);
                IntVar[] scope = {up, lf, cell[r][c], rt, dn};
                store.impose(new Table(scope, shapeTable));
            }
        }

        // No two ships touch, not even diagonally: of two diagonal neighbours at
        // least one is water.
        List<int[]> diagTuples = new ArrayList<>();
        for (int a : codes) {
            for (int b : codes) {
                if (a == water || b == water) {
                    diagTuples.add(new int[]{a, b});
                }
            }
        }
        int[][] diagTable = diagTuples.toArray(new int[0][]);
        for (int r = 0; r + 1 < rows; r++) {
            for (int c = 0; c + 1 < cols; c++) {
                IntVar[] main = {cell[r][c], cell[r + 1][c + 1]};
                store.impose(new Table(main, diagTable));
                IntVar[] anti = {cell[r][c + 1], cell[r + 1][c]};
                store.impose(new Table(anti, diagTable));
            }
        }

        // occ[r][c] = 1 if the cell is occupied by a vessel (a code other than water).
        BooleanVar[][] occ = new BooleanVar[rows][cols];
        List<int[]> occTuples = new ArrayList<>();
        occTuples.add(new int[]{water, 0});
        for (int code : codes) {
            if (code != water) {
                occTuples.add(new int[]{code, 1});
            }
        }
        int[][] occTable = occTuples.toArray(new int[0][]);
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                occ[r][c] = new BooleanVar(store, "occ_" + r + "_" + c);
                IntVar[] pair = {cell[r][c], occ[r][c]};
                store.impose(new Table(pair, occTable));
            }
        }

        // Row and column sums: the number of occupied cells in each row and column.
        int[] ones = new int[Math.max(rows, cols)];
        java.util.Arrays.fill(ones, 1);
        for (int r = 0; r < rows; r++) {
            IntVar[] row = new IntVar[cols];
            for (int c = 0; c < cols; c++) {
                row[c] = occ[r][c];
            }
            store.impose(new LinearInt(row, java.util.Arrays.copyOf(ones, cols), "==", rowSum.getInt(r)));
        }
        for (int c = 0; c < cols; c++) {
            IntVar[] column = new IntVar[rows];
            for (int r = 0; r < rows; r++) {
                column[r] = occ[r][c];
            }
            store.impose(new LinearInt(column, java.util.Arrays.copyOf(ones, rows), "==", colSum.getInt(c)));
        }

        // is[r][c][code] = 1 if the cell has that code. Used to count ships.
        BooleanVar[][][] is = new BooleanVar[rows][cols][maxCode + 1];
        int[] partCodes = {circle, left, right, top, bottom, middle};
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                for (int code : partCodes) {
                    BooleanVar b = new BooleanVar(store, "is_" + r + "_" + c + "_" + code);
                    store.impose(new Reified(new XeqC(cell[r][c], code), b));
                    is[r][c][code] = b;
                }
            }
        }

        // Fleet: for each ship length L, exactly fleet count ships of that length.
        // A submarine is a single CIRCLE cell. A horizontal ship of length L starts at
        // LEFT, has MIDDLE cells in between, and ends at RIGHT; a vertical one is the
        // same with TOP, MIDDLE and BOTTOM. The shape rule makes these runs exact:
        // the ends are bounded by water, so each ship is counted once.
        for (int f = 0; f < fleet.length(); f++) {
            int len = fleet.getJSONArray(f).getInt(0);
            int count = fleet.getJSONArray(f).getInt(1);

            List<IntVar> ships = new ArrayList<>();
            if (len == 1) {
                for (int r = 0; r < rows; r++) {
                    for (int c = 0; c < cols; c++) {
                        ships.add(is[r][c][circle]);
                    }
                }
            } else {
                // horizontal runs starting at column c of row r
                for (int r = 0; r < rows; r++) {
                    for (int c = 0; c + len - 1 < cols; c++) {
                        List<IntVar> lits = new ArrayList<>();
                        lits.add(is[r][c][left]);
                        for (int k = 1; k <= len - 2; k++) {
                            lits.add(is[r][c + k][middle]);
                        }
                        lits.add(is[r][c + len - 1][right]);
                        ships.add(runIndicator(store, lits, len));
                    }
                }
                // vertical runs starting at row r of column c
                for (int c = 0; c < cols; c++) {
                    for (int r = 0; r + len - 1 < rows; r++) {
                        List<IntVar> lits = new ArrayList<>();
                        lits.add(is[r][c][top]);
                        for (int k = 1; k <= len - 2; k++) {
                            lits.add(is[r + k][c][middle]);
                        }
                        lits.add(is[r + len - 1][c][bottom]);
                        ships.add(runIndicator(store, lits, len));
                    }
                }
            }
            if (ships.isEmpty()) {
                if (count > 0) {
                    store.impose(new XeqC(new IntVar(store, 0, 0), 1));
                }
                continue;
            }
            IntVar[] shipVars = ships.toArray(new IntVar[0]);
            int[] shipOnes = new int[shipVars.length];
            java.util.Arrays.fill(shipOnes, 1);
            store.impose(new LinearInt(shipVars, shipOnes, "==", count));
        }

        // Hints: cells given by the puzzle, as [row, col, code].
        for (int h = 0; h < hints.length(); h++) {
            JSONArray hint = hints.getJSONArray(h);
            store.impose(new XeqC(cell[hint.getInt(0)][hint.getInt(1)], hint.getInt(2)));
        }

        // Labels the cell codes; the occupancy and ship indicators follow.
        IntVar[] order = flat.toArray(new IntVar[0]);
        return new Model()
                .put("grid", cell)
                .search(order, null, null);
    }

    // Shape rule for one cell with code s and neighbours up, left, right, down.
    private static boolean shapeValid(int u, int l, int s, int rt, int d,
                                      int water, int circle, int left, int right,
                                      int top, int bottom, int middle) {
        if (s == water) {
            return true;
        }
        if (s == circle) {
            return u == water && l == water && rt == water && d == water;
        }
        if (s == left) {
            return (rt == right || rt == middle) && u == water && d == water && l == water;
        }
        if (s == right) {
            return (l == left || l == middle) && u == water && d == water && rt == water;
        }
        if (s == top) {
            return (d == bottom || d == middle) && u == water && l == water && rt == water;
        }
        if (s == bottom) {
            return (u == top || u == middle) && d == water && l == water && rt == water;
        }
        if (s == middle) {
            boolean horizontal = (l == left || l == middle) && (rt == right || rt == middle)
                    && u == water && d == water;
            boolean vertical = (u == top || u == middle) && (d == bottom || d == middle)
                    && l == water && rt == water;
            return horizontal || vertical;
        }
        return false;
    }

    // A boolean that is 1 exactly when all the given literals are 1 (their count equals len).
    private static BooleanVar runIndicator(Store store, List<IntVar> lits, int len) {
        BooleanVar run = new BooleanVar(store, "run_" + len);
        IntVar[] vars = lits.toArray(new IntVar[0]);
        int[] ones = new int[vars.length];
        java.util.Arrays.fill(ones, 1);
        store.impose(new Reified(new LinearInt(vars, ones, "==", len), run));
        return run;
    }
}
