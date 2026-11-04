// Flow Free: colour every cell of the board with one of the colours, so that each colour forms
// a single pipe that joins its two clue cells. Pipes may not cross or overlap, so each cell has
// exactly one colour. A pipe is a path: an end cell has one neighbour of its colour, every other
// cell of that colour has two. The clue cells are the path ends and are fixed to their colour.
// Connectivity: each clue cell has depth 0, and every other cell of a pipe needs a neighbour of
// the same colour one step closer to a clue cell, so no loop can form.
import org.jacop.constraints.And;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XeqY;
import org.jacop.constraints.XneqY;
import org.jacop.constraints.XplusCeqZ;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray boardJson = inst.getJSONArray("board");
        int n = boardJson.length();
        int[][] clue = new int[n][n];
        int colours = 0;
        for (int i = 0; i < n; i++) {
            JSONArray row = boardJson.getJSONArray(i);
            for (int j = 0; j < n; j++) {
                clue[i][j] = row.getInt(j);
                colours = Math.max(colours, clue[i][j]);
            }
        }

        // colour[i][j] in 1..colours; clue cells are fixed to their colour
        IntVar[][] colour = new IntVar[n][n];
        // depth[i][j]: distance along its pipe from the clue cell the pipe starts from
        IntVar[][] depth = new IntVar[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                String name = i + "_" + j;
                if (clue[i][j] != 0) {
                    colour[i][j] = new IntVar(store, "colour_" + name, clue[i][j], clue[i][j]);
                    depth[i][j] = new IntVar(store, "depth_" + name, 0, 0);
                } else {
                    colour[i][j] = new IntVar(store, "colour_" + name, 1, colours);
                    depth[i][j] = new IntVar(store, "depth_" + name, 0, n * n);
                }
            }
        }

        // the four neighbours of each cell
        int[] dr = {-1, 1, 0, 0};
        int[] dc = {0, 0, -1, 1};

        // same[i][j][d]: the neighbour of (i,j) in direction d has the same colour as (i,j).
        // It is one boolean per undirected pair, shared by both cells
        BooleanVar[][][] same = new BooleanVar[n][n][4];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                for (int d = 0; d < 4; d++) {
                    int a = i + dr[d], b = j + dc[d];
                    if (a < 0 || a >= n || b < 0 || b >= n) {
                        continue;
                    }
                    if (same[a][b][d ^ 1] != null) {
                        same[i][j][d] = same[a][b][d ^ 1];
                        continue;
                    }
                    BooleanVar s = new BooleanVar(store, "same_" + i + "_" + j + "_" + d);
                    store.impose(new Reified(new XeqY(colour[i][j], colour[a][b]), s));
                    same[i][j][d] = s;
                }
            }
        }

        // a cell is a pipe end (clue) or a pipe middle; a pipe end has one neighbour of its colour,
        // a middle cell has two; every middle cell also needs a same-colour neighbour one step
        // closer to the clue cell it grows from
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                IntVar[] neighbours = new IntVar[4];
                int[] ones = new int[4];
                int count = 0;
                BooleanVar[] sameList = new BooleanVar[4];
                int sameCount = 0;
                for (int d = 0; d < 4; d++) {
                    if (same[i][j][d] != null) {
                        sameList[sameCount++] = same[i][j][d];
                    }
                }
                BooleanVar[] sameArr = new BooleanVar[sameCount];
                int[] sameOnes = new int[sameCount];
                for (int k = 0; k < sameCount; k++) {
                    sameArr[k] = sameList[k];
                    sameOnes[k] = 1;
                }

                if (clue[i][j] != 0) {
                    // a pipe end has exactly one neighbour of its colour
                    store.impose(new LinearInt(sameArr, sameOnes, "==", 1));
                } else {
                    // a middle cell has exactly two neighbours of its colour
                    store.impose(new LinearInt(sameArr, sameOnes, "==", 2));

                    // and one same-colour neighbour one step closer to the clue cell:
                    // parent[d] = the neighbour in direction d has the same colour and depth one less
                    BooleanVar[] parents = new BooleanVar[4];
                    int parentCount = 0;
                    for (int d = 0; d < 4; d++) {
                        int a = i + dr[d], b = j + dc[d];
                        if (a < 0 || a >= n || b < 0 || b >= n) {
                            continue;
                        }
                        BooleanVar p = new BooleanVar(store, "parent_" + i + "_" + j + "_" + d);
                        store.impose(new Reified(
                            new And(new XeqY(colour[i][j], colour[a][b]),
                                    new XplusCeqZ(depth[a][b], 1, depth[i][j])),
                            p));
                        parents[parentCount++] = p;
                    }
                    BooleanVar[] parentArr = new BooleanVar[parentCount];
                    int[] parentOnes = new int[parentCount];
                    for (int k = 0; k < parentCount; k++) {
                        parentArr[k] = parents[k];
                        parentOnes[k] = 1;
                    }
                    store.impose(new LinearInt(parentArr, parentOnes, ">=", 1));
                }
            }
        }

        // label the colours first, then the depths; the pipes follow from them
        IntVar[] decisions = new IntVar[2 * n * n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                decisions[i * n + j] = colour[i][j];
                decisions[n * n + i * n + j] = depth[i][j];
            }
        }

        Model model = new Model().put("B", colour);
        return model.search(decisions, null, null);
    }
}
