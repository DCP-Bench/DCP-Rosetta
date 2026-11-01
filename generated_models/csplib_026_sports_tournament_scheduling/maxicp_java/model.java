import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Sports tournament scheduling (CSPLib 026): n teams, n-1 weeks of n/2 periods, one game per
// period and week; every team plays once a week, at most twice in the same period over the
// tournament, and every other team exactly once. home[w][p] / away[w][p] are the two teams of the
// game in week w and period p, numbered from 1 to n.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n_teams");
    int weeks = n - 1, periods = n / 2;
    CPSolver cp = m.cp();

    // game ids: one per unordered pair of teams {a, b}; the table lists (home, away, id) for both
    // orientations
    int nGames = n * (n - 1) / 2;
    int[][] pairTable = new int[2 * nGames][];
    int g = 0, row = 0;
    for (int a = 1; a <= n; a++)
      for (int b = a + 1; b <= n; b++) {
        pairTable[row++] = new int[]{a, b, g};
        pairTable[row++] = new int[]{b, a, g};
        g++;
      }

    // An extra "dummy" week is added (Regin's model): with n-1 weeks and at most two games per
    // period, every team plays exactly one period only once, and in each period exactly two teams do;
    // pairing those two in the dummy week makes every team play exactly twice in every period.
    // Any tournament extends this way, so no solution is lost.
    int allWeeks = weeks + 1;

    // flip[w][p]: whether the home team has the larger number. No rule depends on which team of a
    // game is at home, so these are registered first: the search fixes them (smaller number at
    // home first) before it looks for the games, and never re-explores a failed set of games under
    // the other orientation. Both orientations stay allowed.
    CPBoolVar[][] flip = new CPBoolVar[allWeeks][periods];
    for (int w = 0; w < allWeeks; w++) flip[w] = m.boolVarArray(periods);
    CPIntVar[][] home = new CPIntVar[allWeeks][periods], away = new CPIntVar[allWeeks][periods], game = new CPIntVar[allWeeks][periods];
    for (int w = 0; w < allWeeks; w++)
      for (int p = 0; p < periods; p++) {
        home[w][p] = m.intVar(1, n);
        away[w][p] = m.intVar(1, n);
        game[w][p] = makeIntVar(cp, 0, nGames - 1);
        // the slot holds a game between two different teams, and its id names the pair
        cp.post(table(new CPIntVar[]{home[w][p], away[w][p], game[w][p]}, pairTable));
        cp.post(eq(flip[w][p], isGt(home[w][p], away[w][p])));
      }

    // every team plays every other team exactly once: the games of the real weeks are all different
    // (there are exactly as many slots as pairs)
    CPIntVar[] realGames = new CPIntVar[weeks * periods];
    for (int w = 0; w < weeks; w++)
      for (int p = 0; p < periods; p++) realGames[w * periods + p] = game[w][p];
    cp.post(allDifferent(realGames));

    // every team plays once a week (in the dummy week too)
    for (int w = 0; w < allWeeks; w++) {
      CPIntVar[] teams = new CPIntVar[n];
      for (int p = 0; p < periods; p++) {
        teams[2 * p] = home[w][p];
        teams[2 * p + 1] = away[w][p];
      }
      cp.post(allDifferent(teams));
    }

    // every team plays at most twice in the same period; with the dummy week, exactly twice
    for (int p = 0; p < periods; p++) {
      CPIntVar[] slots = new CPIntVar[2 * allWeeks];
      for (int w = 0; w < allWeeks; w++) {
        slots[2 * w] = home[w][p];
        slots[2 * w + 1] = away[w][p];
      }
      for (int t = 1; t <= n; t++) {
        CPBoolVar[] plays = new CPBoolVar[slots.length];
        for (int k = 0; k < slots.length; k++) plays[k] = isEq(slots[k], t);
        cp.post(sum(plays, 2));
      }
    }

    CPIntVar[][] homeOut = new CPIntVar[weeks][], awayOut = new CPIntVar[weeks][];
    for (int w = 0; w < weeks; w++) {
      homeOut[w] = home[w];
      awayOut[w] = away[w];
    }
    out.put("home", homeOut);
    out.put("away", awayOut);
  }
}
