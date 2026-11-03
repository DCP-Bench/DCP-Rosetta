// Minesweeper: decide which unopened cells hold a mine, from the numbers shown on the opened cells.
// Each opened cell is safe (no mine), and its number is the count of mines among its 8 neighbours.
// Unopened cells are marked with the instance's X value; their mine status is the unknown.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int unknown = inst.getInt("X");
        JSONArray board = inst.getJSONArray("game_data");
        int rows = board.length();
        int cols = board.getJSONArray(0).length();

        // mines[r][c] = 1 when the cell at row r, column c holds a mine.
        BooleanVar[][] mines = new BooleanVar[rows][cols];
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                mines[r][c] = new BooleanVar(store, "mine" + r + "_" + c);
            }
        }

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                int clue = board.getJSONArray(r).getInt(c);
                if (clue == unknown) continue;

                // An opened cell is safe.
                store.impose(new XeqC(mines[r][c], 0));

                // The number on an opened cell counts the mines in its neighbourhood.
                int count = 0;
                for (int dr = -1; dr <= 1; dr++) {
                    for (int dc = -1; dc <= 1; dc++) {
                        if (dr == 0 && dc == 0) continue;
                        int nr = r + dr, nc = c + dc;
                        if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
                        count++;
                    }
                }
                IntVar[] neighbours = new IntVar[count];
                int[] ones = new int[count];
                int k = 0;
                for (int dr = -1; dr <= 1; dr++) {
                    for (int dc = -1; dc <= 1; dc++) {
                        if (dr == 0 && dc == 0) continue;
                        int nr = r + dr, nc = c + dc;
                        if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
                        neighbours[k] = mines[nr][nc];
                        ones[k] = 1;
                        k++;
                    }
                }
                store.impose(new LinearInt(neighbours, ones, "==", clue));
            }
        }

        return new Model().put("mines", mines);
    }
}
