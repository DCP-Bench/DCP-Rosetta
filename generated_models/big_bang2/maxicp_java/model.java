import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Nontransitive dice for Rock-Paper-Scissors-Lizard-Spock: five six-sided dice with faces in
// 1..12 such that each die beats exactly the two dice its choice beats in the game, where die A
// beats die B when A shows the strictly larger face in more than half of the 36 face pairs.
public class Submission {
  // the ten "beats" relations of the game, as (winner, loser) with Rock 0, Paper 1, Scissors 2,
  // Lizard 3, Spock 4 (fixed by the problem statement)
  static final int[][] BEATS = {
    {0, 2}, {0, 3}, {1, 0}, {1, 4}, {2, 1}, {2, 3}, {3, 1}, {3, 4}, {4, 0}, {4, 2}};

  public static void build(Instance inst, Model m, Outputs out) {
    final int dice = 5, faces = 6, low = 1, high = 12;
    CPSolver cp = m.cp();

    // dice[d][k]: face k of die d, in 1..12 (values may repeat). A die is a multiset of faces,
    // so its faces are listed in nondecreasing order; any die can be written this way, so no
    // set of dice is lost, and the search does not revisit the 6! orders of the same die.
    CPIntVar[][] face = new CPIntVar[dice][faces];
    for (int d = 0; d < dice; d++)
      for (int k = 0; k < faces; k++) face[d][k] = m.intVar(low, high);
    for (int d = 0; d < dice; d++)
      for (int k = 0; k + 1 < faces; k++) cp.post(le(face[d][k], face[d][k + 1]));

    // below[d][v]: how many faces of die d are strictly below v, for v in 0..12
    CPIntVar[][] below = new CPIntVar[dice][high + 1];
    for (int d = 0; d < dice; d++)
      for (int v = 0; v <= high; v++) {
        CPBoolVar[] lower = new CPBoolVar[faces];
        for (int k = 0; k < faces; k++) lower[k] = isLt(face[d][k], v);
        below[d][v] = sum(lower);
      }

    // die a beats die b: the number of face pairs where a's face is strictly larger is more
    // than half of 36, that is at least 19. Face k of a beats exactly below[b][face] faces of b.
    for (int[] rel : BEATS) {
      int a = rel[0], b = rel[1];
      CPIntVar[] wins = new CPIntVar[faces];
      for (int k = 0; k < faces; k++) wins[k] = element(below[b], face[a][k]);
      cp.post(ge(sum(wins), faces * faces / 2 + 1));
      // Implied by the sorted faces (face k counted from 1): the faces of a beat a nondecreasing
      // number of b's faces, so a's first k faces beat at most k times what face k beats and the
      // other 6 - k faces at most 6 each. Reaching 19 thus needs face k to beat at least
      // need = ceil((19 - 6 (6 - k)) / k) faces of b, that is, to be larger than b's face number need.
      for (int k = 1; k <= faces; k++) {
        int rest = faces * faces / 2 + 1 - faces * (faces - k);
        if (rest <= 0) continue;
        int need = (rest + k - 1) / k;
        cp.post(gt(face[a][k - 1], face[b][need - 1]));
      }
    }

    out.put("dice", face);
  }
}
