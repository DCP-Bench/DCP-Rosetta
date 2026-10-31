import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Maximum density still life (CSPLib 032): choose live and dead cells on an n x m grid (everything
// outside it dead) so that the pattern never changes: a live cell has 2 or 3 live neighbours, a
// dead cell (outside cells included) does not have exactly 3; maximise the live cells.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n"), cols = inst.getInt("m");
    CPSolver cp = m.cp();

    // live[r][c]: whether cell (r, c) of the grid is alive. Each is the negation of a registered
    // Boolean, so the search, which tries 0 first, tries a live cell first.
    CPBoolVar[][] live = new CPBoolVar[n][cols];
    for (int r = 0; r < n; r++)
      for (int c = 0; c < cols; c++) live[r][c] = not(m.boolVar());

    // the board with a ring of dead cells around the grid (cells further out have no live neighbour)
    CPIntVar dead = makeIntVar(cp, 0, 0);
    CPIntVar[][] board = new CPIntVar[n + 2][cols + 2];
    for (int r = 0; r < n + 2; r++)
      for (int c = 0; c < cols + 2; c++)
        board[r][c] = (r >= 1 && r <= n && c >= 1 && c <= cols) ? live[r - 1][c - 1] : dead;

    // the rules, for every grid cell and every dead cell just outside: (cell, live neighbours) is
    // live with 2 or 3, or dead with anything but 3
    int[][] rule = new int[10][];
    int k = 0;
    for (int s = 0; s <= 8; s++) if (s != 3) rule[k++] = new int[]{0, s};
    rule[k++] = new int[]{1, 2};
    rule[k] = new int[]{1, 3};
    for (int r = 0; r < n + 2; r++)
      for (int c = 0; c < cols + 2; c++) {
        List<CPIntVar> around = new ArrayList<>();
        for (int dr = -1; dr <= 1; dr++)
          for (int dc = -1; dc <= 1; dc++) {
            int rr = r + dr, cc = c + dc;
            if ((dr != 0 || dc != 0) && rr >= 1 && rr <= n && cc >= 1 && cc <= cols) around.add(live[rr - 1][cc - 1]);
          }
        if (around.isEmpty()) continue;
        CPIntVar count = sum(around.toArray(new CPIntVar[0]));
        cp.post(table(new CPIntVar[]{board[r][c], count}, rule));
      }

    // Implied by the rules: any 3 x 3 square of the board holds at most 6 live cells. (Checked
    // exhaustively: no 3 x 3 pattern with 7 or more live cells has every cell obey the rules,
    // whatever the cells around it.) The objective is written as sums over squares that tile the
    // grid, in several placements of the tiling, so each square's bound limits it during search.
    CPIntVar[] all = new CPIntVar[n * cols];
    for (int r = 0; r < n; r++)
      for (int c = 0; c < cols; c++) all[r * cols + c] = live[r][c];
    CPIntVar total = sum(all);
    for (int r = 0; r + 3 <= n; r++)
      for (int c = 0; c + 3 <= cols; c++) {
        CPIntVar[] square = new CPIntVar[9];
        for (int i = 0; i < 9; i++) square[i] = live[r + i / 3][c + i % 3];
        cp.post(le(sum(square), 6));
      }
    for (int offR = 0; offR < 3; offR++)
      for (int offC = 0; offC < 3; offC++) {
        List<CPIntVar> blocks = new ArrayList<>();
        for (int r0 = offR - 3; r0 < n; r0 += 3)
          for (int c0 = offC - 3; c0 < cols; c0 += 3) {
            List<CPIntVar> cells = new ArrayList<>();
            for (int r = Math.max(0, r0); r < Math.min(n, r0 + 3); r++)
              for (int c = Math.max(0, c0); c < Math.min(cols, c0 + 3); c++) cells.add(live[r][c]);
            if (cells.isEmpty()) continue;
            CPIntVar block = sum(cells.toArray(new CPIntVar[0]));
            if (cells.size() == 9) cp.post(le(block, 6));
            blocks.add(block);
          }
        cp.post(eq(total, sum(blocks.toArray(new CPIntVar[0]))));
      }

    // maximise the live cells
    m.maximize(total);
    out.put("grid", live);
  }
}
