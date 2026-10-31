import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// ACC basketball schedule 1997/98 (CSPLib 011): a mirrored double round-robin timetable for the
// nine Atlantic Coast Conference teams over 18 dates, with the venue, pattern, weekend, rival and
// opponent-sequence rules of Nemhauser and Trick. config[d][i] is the opponent of team i on date d
// (team i itself on a bye), where[d][i] is 0 at home, 1 bye, 2 away.
public class Submission {
  // the teams in the order of the statement, numbered from 0
  static final int CLEM = 0, DUKE = 1, FSU = 2, GT = 3, UMD = 4, UNC = 5, NCST = 6, UVA = 7, WAKE = 8;
  static final int HOME = 0, BYE = 1, AWAY = 2;

  public static void build(Instance inst, Model m, Outputs out) {
    int nTeams = inst.getInt("n_teams");
    int nDays = inst.getInt("n_days");
    CPSolver cp = m.cp();

    // 1. The mirroring scheme of the statement (dates from 1): the same two teams meet on both
    // dates of a pair, once at home and once away, so the 18 dates form 9 rounds.
    int[][] mirror = {{1, 8}, {2, 9}, {3, 12}, {4, 13}, {5, 14}, {6, 15}, {7, 16}, {10, 17}, {11, 18}};
    int nRounds = mirror.length;
    int[] roundOf = new int[nDays];
    boolean[] firstOfRound = new boolean[nDays];
    for (int r = 0; r < nRounds; r++) {
      roundOf[mirror[r][0] - 1] = r;
      roundOf[mirror[r][1] - 1] = r;
      firstOfRound[mirror[r][0] - 1] = true;
    }

    // venue[r][i]: where team i is on the first date of round r (home, bye or away); these are
    // registered first, so the search fixes the home/away/bye pattern before the opponents
    CPIntVar[][] venue = new CPIntVar[nRounds][nTeams];
    for (int r = 0; r < nRounds; r++) venue[r] = m.intVarArray(nTeams, HOME, AWAY);
    // opp[r][i]: the opponent of team i in round r, i itself for a bye
    CPIntVar[][] opp = new CPIntVar[nRounds][nTeams];
    for (int r = 0; r < nRounds; r++) opp[r] = m.intVarArray(nTeams, 0, nTeams - 1);

    // where and config per date: the second date of a round mirrors the first, with the venue
    // swapped (home 0 <-> away 2, a bye stays a bye)
    CPIntVar[][] where = new CPIntVar[nDays][];
    CPIntVar[][] config = new CPIntVar[nDays][];
    for (int d = 0; d < nDays; d++) {
      int r = roundOf[d];
      config[d] = opp[r];
      if (firstOfRound[d]) where[d] = venue[r];
      else {
        where[d] = new CPIntVar[nTeams];
        for (int i = 0; i < nTeams; i++) where[d][i] = plus(minus(venue[r][i]), AWAY);
      }
    }

    for (int r = 0; r < nRounds; r++) {
      for (int i = 0; i < nTeams; i++) {
        // the opponent of my opponent is me (a round is a matching, a bye pairs a team with itself)
        cp.post(eq(element(opp[r], opp[r][i]), i));
        // a team has a bye exactly when it is paired with itself
        CPBoolVar bye = isEq(opp[r][i], i);
        cp.post(eq(bye, isEq(venue[r][i], BYE)));
        // when two teams meet, one is at home and the other away
        for (int j = 0; j < nTeams; j++) {
          if (j == i) continue;
          CPBoolVar meet = isEq(opp[r][i], j);
          cp.post(implies(meet, isEq(sum(venue[r][i], venue[r][j]), HOME + AWAY)));
        }
      }
      // with nine teams, exactly one team has a bye in each round, and four play at home
      CPBoolVar[] byes = new CPBoolVar[nTeams], homes = new CPBoolVar[nTeams];
      for (int i = 0; i < nTeams; i++) {
        byes[i] = isEq(venue[r][i], BYE);
        homes[i] = isEq(venue[r][i], HOME);
      }
      cp.post(sum(byes, 1));
      cp.post(sum(homes, (nTeams - 1) / 2));
    }
    // double round-robin: over the rounds each team meets every other team once (and itself,
    // the bye, once), so a team's opponents over the rounds are all different
    for (int i = 0; i < nTeams; i++) {
      CPIntVar[] mine = new CPIntVar[nRounds];
      for (int r = 0; r < nRounds; r++) mine[r] = opp[r][i];
      cp.post(allDifferent(mine));
    }

    // per-date indicators of home, away and bye
    CPBoolVar[][] home = new CPBoolVar[nDays][nTeams], away = new CPBoolVar[nDays][nTeams], bye = new CPBoolVar[nDays][nTeams];
    for (int d = 0; d < nDays; d++)
      for (int i = 0; i < nTeams; i++) {
        home[d][i] = isEq(where[d][i], HOME);
        away[d][i] = isEq(where[d][i], AWAY);
        bye[d][i] = isEq(where[d][i], BYE);
      }

    for (int i = 0; i < nTeams; i++) {
      // 2. no team plays away on both last dates
      cp.post(le(sum(away[nDays - 2][i], away[nDays - 1][i]), 1));
      // 3. at most two away matches in a row, at most two home matches in a row, at most three
      // away matches or byes in a row, at most four home matches or byes in a row
      for (int d = 0; d + 3 <= nDays; d++) {
        cp.post(le(sum(away[d][i], away[d + 1][i], away[d + 2][i]), 2));
        cp.post(le(sum(home[d][i], home[d + 1][i], home[d + 2][i]), 2));
      }
      for (int d = 0; d + 4 <= nDays; d++)   // away or bye is "not home"
        cp.post(ge(sum(home[d][i], home[d + 1][i], home[d + 2][i], home[d + 3][i]), 1));
      for (int d = 0; d + 5 <= nDays; d++)   // home or bye is "not away"
        cp.post(ge(sum(away[d][i], away[d + 1][i], away[d + 2][i], away[d + 3][i], away[d + 4][i]), 1));
      // 4. of the weekends (even dates), four at home, four away and one bye
      int nWeekends = nDays / 2;
      CPBoolVar[] wHome = new CPBoolVar[nWeekends], wAway = new CPBoolVar[nWeekends], wBye = new CPBoolVar[nWeekends];
      for (int w = 0; w < nWeekends; w++) {
        wHome[w] = home[2 * w + 1][i];
        wAway[w] = away[2 * w + 1][i];
        wBye[w] = bye[2 * w + 1][i];
      }
      cp.post(sum(wHome, 4));
      cp.post(sum(wAway, 4));
      cp.post(sum(wBye, 1));
      // 5. home matches or byes on at least two of the first five weekends
      cp.post(le(sum(wAway[0], wAway[1], wAway[2], wAway[3], wAway[4]), 3));
    }

    // 6. on the last date every team except FSU plays its rival, unless it plays FSU or has a bye
    int[][] rivals = {{DUKE, UNC}, {CLEM, GT}, {NCST, WAKE}, {UMD, UVA}};
    CPIntVar[] last = config[nDays - 1];
    for (int[] pair : rivals)
      for (int k = 0; k < 2; k++) {
        int t = pair[k], rival = pair[1 - k];
        cp.post(or(isEq(last[t], rival), isEq(last[t], FSU), isEq(last[t], t)));
      }

    // 7. Wake-UNC, Wake-Duke, GT-UNC and GT-Duke meet at least once in dates 11 to 18
    int[][] late = {{WAKE, UNC}, {WAKE, DUKE}, {GT, UNC}, {GT, DUKE}};
    for (int[] pair : late) {
      CPBoolVar[] meets = new CPBoolVar[nDays - 10];
      for (int d = 10; d < nDays; d++) meets[d - 10] = isEq(config[d][pair[0]], pair[1]);
      cp.post(or(meets));
    }

    // 8. no team plays away against UNC and Duke on two consecutive dates (in either order), and
    // no team plays UNC, Duke and Wake on three consecutive dates (in any order)
    for (int i = 0; i < nTeams; i++) {
      for (int d = 0; d + 1 < nDays; d++) {
        cp.post(or(not(away[d][i]), not(away[d + 1][i]), not(isEq(config[d][i], UNC)), not(isEq(config[d + 1][i], DUKE))));
        cp.post(or(not(away[d][i]), not(away[d + 1][i]), not(isEq(config[d][i], DUKE)), not(isEq(config[d + 1][i], UNC))));
      }
      for (int d = 0; d + 2 < nDays; d++) {
        CPBoolVar[] strong = new CPBoolVar[3];
        for (int k = 0; k < 3; k++)
          strong[k] = isOr(isEq(config[d + k][i], UNC), isEq(config[d + k][i], DUKE), isEq(config[d + k][i], WAKE));
        cp.post(le(sum(strong), 2));
      }
    }

    // 9. the other fixed requirements (dates from 1)
    cp.post(eq(config[17][UNC], DUKE));              // UNC plays Duke on the last date
    cp.post(eq(config[10][UNC], DUKE));              // and on date 11
    cp.post(eq(config[1][UNC], CLEM));               // UNC plays Clem on date 2
    cp.post(eq(where[15][DUKE], BYE));               // Duke has a bye on date 16
    cp.post(neq(where[16][WAKE], HOME));             // Wake does not play home on date 17
    cp.post(eq(where[0][WAKE], BYE));                // Wake has a bye on date 1
    for (int t : new int[]{CLEM, DUKE, UMD, WAKE}) cp.post(neq(where[17][t], AWAY));  // not away on the last date
    for (int t : new int[]{CLEM, FSU, GT, WAKE}) cp.post(neq(where[0][t], AWAY));     // not away on date 1
    for (int t : new int[]{FSU, NCST}) cp.post(neq(where[17][t], BYE));               // no bye on the last date
    cp.post(neq(where[0][UNC], BYE));                // UNC has no bye on date 1

    out.put("config", config);
    out.put("where", where);
  }
}
