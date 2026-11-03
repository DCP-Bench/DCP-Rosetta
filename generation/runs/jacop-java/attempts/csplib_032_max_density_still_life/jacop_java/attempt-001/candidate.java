// Maximum-density still life (Conway's Game of Life) on an n x m active grid: choose live/dead
// cells so that the pattern does not change in one generation and has as many live cells as possible.
// Output "grid" is n rows of m booleans (true = live). Cells outside the grid are dead.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XgteqC;
import org.jacop.constraints.XlteqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        int m = inst.getInt("m");

        // Padded board of (n+2) x (m+2) cells. The inner n x m cells are the active grid; the
        // ring around them is dead and fixed to the constant 0 (so its neighbours are counted correctly).
        IntVar[][] p = new IntVar[n + 2][m + 2];
        BooleanVar[][] grid = new BooleanVar[n][m];
        IntVar[] gridFlat = new IntVar[n * m];
        for (int i = 0; i < n + 2; i++) {
            for (int j = 0; j < m + 2; j++) {
                if (i >= 1 && i <= n && j >= 1 && j <= m) {
                    BooleanVar b = new BooleanVar(store, "cell_" + (i - 1) + "_" + (j - 1));
                    p[i][j] = b;
                    grid[i - 1][j - 1] = b;
                    gridFlat[(i - 1) * m + (j - 1)] = b;
                } else {
                    p[i][j] = new IntVar(store, 0, 0);
                }
            }
        }

        // Still-life rules for every padded cell, including the dead ring. Let s be the number of
        // live neighbours (the 8 surrounding cells) and c the cell's own state.
        for (int i = 0; i < n + 2; i++) {
            for (int j = 0; j < m + 2; j++) {
                IntVar c = p[i][j];

                // Collect the live-neighbour count s = sum of the in-range neighbours.
                int count = 0;
                for (int di = -1; di <= 1; di++) {
                    for (int dj = -1; dj <= 1; dj++) {
                        if (di == 0 && dj == 0) continue;
                        if (i + di >= 0 && i + di < n + 2 && j + dj >= 0 && j + dj < m + 2) count++;
                    }
                }
                IntVar[] vars = new IntVar[count + 1];
                int[] weights = new int[count + 1];
                int k = 0;
                for (int di = -1; di <= 1; di++) {
                    for (int dj = -1; dj <= 1; dj++) {
                        if (di == 0 && dj == 0) continue;
                        if (i + di >= 0 && i + di < n + 2 && j + dj >= 0 && j + dj < m + 2) {
                            vars[k] = p[i + di][j + dj];
                            weights[k] = 1;
                            k++;
                        }
                    }
                }
                IntVar s = new IntVar(store, 0, 8);
                vars[count] = s;
                weights[count] = -1;
                store.impose(new LinearInt(vars, weights, "==", 0));

                // A dead cell must not have exactly 3 live neighbours: (s == 3) implies c is live.
                BooleanVar eq3 = new BooleanVar(store, "eq3_" + i + "_" + j);
                store.impose(new Reified(new XeqC(s, 3), eq3));
                store.impose(new LinearInt(new IntVar[]{eq3, c}, new int[]{1, -1}, "<=", 0));

                // A live cell must have 2 or 3 live neighbours: not (c and s <= 1), not (c and s >= 4).
                BooleanVar few = new BooleanVar(store, "few_" + i + "_" + j);
                store.impose(new Reified(new XlteqC(s, 1), few));
                store.impose(new LinearInt(new IntVar[]{few, c}, new int[]{1, 1}, "<=", 1));

                BooleanVar many = new BooleanVar(store, "many_" + i + "_" + j);
                store.impose(new Reified(new XgteqC(s, 4), many));
                store.impose(new LinearInt(new IntVar[]{many, c}, new int[]{1, 1}, "<=", 1));
            }
        }

        // Objective: the number of live cells in the active grid.
        IntVar total = new IntVar(store, 0, n * m);
        IntVar[] sumVars = new IntVar[n * m + 1];
        int[] sumWeights = new int[n * m + 1];
        for (int t = 0; t < n * m; t++) {
            sumVars[t] = gridFlat[t];
            sumWeights[t] = 1;
        }
        sumVars[n * m] = total;
        sumWeights[n * m] = -1;
        store.impose(new LinearInt(sumVars, sumWeights, "==", 0));

        // The grid cells are the decisions: label them first, the helper flags after.
        return new Model().put("grid", grid).search(gridFlat, null, null).maximize(total);
    }
}
