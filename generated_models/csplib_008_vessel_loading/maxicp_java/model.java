import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Vessel loading (CSPLib 008): place the containers on the rectangular deck, each parallel to the
// sides (possibly turned by 90 degrees), without overlap, and with containers of certain classes
// at least the given separation apart along or across the deck. left/right are a container's
// extent across the deck width (right = left + its extent), bottom/top along the deck length.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int deckW = inst.getInt("deck_width"), deckL = inst.getInt("deck_length");
    int n = inst.getInt("n_containers");
    int[] width = inst.getIntArray("width"), length = inst.getIntArray("length");
    int[] cls = inst.getIntArray("classes");
    int[][] sep = inst.getIntMatrix("separation");
    CPSolver cp = m.cp();

    // turned[c]: container c lies turned, its length across the deck width
    CPBoolVar[] turned = new CPBoolVar[n];
    for (int c = 0; c < n; c++) turned[c] = makeBoolVar(cp);
    CPIntVar[] left = new CPIntVar[n], bottom = new CPIntVar[n], right = new CPIntVar[n], top = new CPIntVar[n];
    CPIntVar[] across = new CPIntVar[n], along = new CPIntVar[n];
    for (int c = 0; c < n; c++) {
      // its extent across the width and along the length, after turning
      across[c] = plus(mul(turned[c], length[c] - width[c]), width[c]);
      along[c] = plus(mul(turned[c], width[c] - length[c]), length[c]);
      // it lies on the deck
      left[c] = makeIntVar(cp, 0, deckW - Math.min(width[c], length[c]));
      bottom[c] = makeIntVar(cp, 0, deckL - Math.min(width[c], length[c]));
      right[c] = sum(left[c], across[c]);
      top[c] = sum(bottom[c], along[c]);
      cp.post(le(right[c], deckW));
      cp.post(le(top[c], deckL));
    }

    int area = 0;
    for (int c = 0; c < n; c++) area += width[c] * length[c];
    boolean full = area == deckW * deckL;

    // on[x][y][c]: container c covers the unit cell (x, y) of the deck. These are the decisions,
    // registered cell by cell from the bottom-left corner, row by row; every one is a Boolean, so
    // firstFailBinary takes them in that order, each the negation of a registered Boolean so that
    // "c covers this cell" is tried first: the search fills the deck from its lowest, leftmost free
    // cell, as a bottom-left packing would. A cell holds at most one container.
    for (int y = 0; y < deckL; y++)
      for (int x = 0; x < deckW; x++) {
        CPBoolVar[] on = new CPBoolVar[n];
        for (int c = 0; c < n; c++) {
          on[c] = not(m.boolVar());
          cp.post(eq(on[c], not(isOr(not(covers(left[c], right[c], x)), not(covers(bottom[c], top[c], y))))));
        }
        // when the containers' areas fill the deck exactly, every cell is covered
        if (full) cp.post(sum(on, 1)); else cp.post(le(sum(on), 1));
      }

    // two containers do not overlap, and those of classes with a separation s are at least s apart
    // along or across the deck: one lies at least s left of, right of, below or above the other
    for (int a = 0; a < n; a++)
      for (int b = a + 1; b < n; b++) {
        int s = sep[cls[a] - 1][cls[b] - 1];
        cp.post(or(isLe(plus(right[a], s), left[b]), isLe(plus(right[b], s), left[a]),
                   isLe(plus(top[a], s), bottom[b]), isLe(plus(top[b], s), bottom[a])));
      }

    // Implied by the no-overlap: the containers crossing any unit-wide strip of the deck occupy at
    // most its length (or width) together; when their areas fill the deck exactly, exactly that.
    for (int x = 0; x < deckW; x++) {
      CPIntVar[] used = new CPIntVar[n];
      for (int c = 0; c < n; c++) used[c] = mul(along[c], covers(left[c], right[c], x));
      if (full) cp.post(eq(sum(used), deckL)); else cp.post(le(sum(used), deckL));
    }
    for (int y = 0; y < deckL; y++) {
      CPIntVar[] used = new CPIntVar[n];
      for (int c = 0; c < n; c++) used[c] = mul(across[c], covers(bottom[c], top[c], y));
      if (full) cp.post(eq(sum(used), deckW)); else cp.post(le(sum(used), deckW));
    }

    out.put("left", left);
    out.put("right", right);
    out.put("bottom", bottom);
    out.put("top", top);
  }

  // whether a container spanning [lo, hi) covers the unit strip [x, x + 1)
  static CPBoolVar covers(CPIntVar lo, CPIntVar hi, int x) {
    return not(isOr(not(isLe(lo, x)), isLe(hi, x)));
  }
}
