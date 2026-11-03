// Sports tournament scheduling: n teams play over n-1 weeks. Each week is split into n/2
// periods, and each period into a home slot and an away slot. Teams are numbered 1..n.
// home[w][p] and away[w][p] are the teams in the two slots of period p in week w.
// The tournament must satisfy three constraints:
//   1. every team plays once a week;
//   2. every team plays at most twice in the same period over the tournament;
//   3. every team plays every other team exactly once.
import org.jacop.constraints.*;
import org.jacop.constraints.table.Table;
import org.jacop.core.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // the number of teams comes from the instance; weeks and periods follow from it
        int n = inst.getInt("n_teams");
        int weeks = n - 1;
        int periods = n / 2;

        // home[w][p] and away[w][p]: the two teams of period p in week w, numbered 1..n
        IntVar[][] home = new IntVar[weeks][periods];
        IntVar[][] away = new IntVar[weeks][periods];
        for (int w = 0; w < weeks; w++) {
            for (int p = 0; p < periods; p++) {
                home[w][p] = new IntVar(store, "home" + (w + 1) + "_" + (p + 1), 1, n);
                away[w][p] = new IntVar(store, "away" + (w + 1) + "_" + (p + 1), 1, n);
                // the two teams of one period are different teams
                store.impose(new XneqY(home[w][p], away[w][p]));
            }
        }

        // constraint 1: every team plays once a week, so the n slots of a week hold each team once
        for (int w = 0; w < weeks; w++) {
            IntVar[] week = new IntVar[n];
            for (int p = 0; p < periods; p++) {
                week[2 * p] = home[w][p];
                week[2 * p + 1] = away[w][p];
            }
            store.impose(new Alldistinct(week));
        }

        // constraint 2: each team plays at most twice in the same period over the tournament
        // inPeriod lists the team in each slot of period p over all weeks
        for (int p = 0; p < periods; p++) {
            for (int t = 1; t <= n; t++) {
                IntVar[] inPeriod = new IntVar[2 * weeks];
                for (int w = 0; w < weeks; w++) {
                    inPeriod[2 * w] = home[w][p];
                    inPeriod[2 * w + 1] = away[w][p];
                }
                IntVar times = new IntVar(store, 0, 2 * weeks);
                store.impose(new Count(inPeriod, times, t));
                store.impose(new XlteqC(times, 2));
            }
        }

        // constraint 3: every team plays every other team exactly once.
        // opp[t][w] is the opponent of team t in week w. Team t plays once a week, so it is
        // the other team of t's slot pair in that week; then each team's opponents over the
        // n-1 weeks are all different, and they are all the other n-1 teams.
        IntVar[][] opp = new IntVar[n + 1][weeks];
        for (int t = 1; t <= n; t++) {
            for (int w = 0; w < weeks; w++) {
                opp[t][w] = new IntVar(store, "opp" + t + "_" + (w + 1), 1, n);
                store.impose(new XneqC(opp[t][w], t));
            }
            for (int w = 0; w < weeks; w++) {
                for (int p = 0; p < periods; p++) {
                    // if t is at home in this period, the opponent is the away team, and vice versa
                    store.impose(new IfThen(new XeqC(home[w][p], t), new XeqY(opp[t][w], away[w][p])));
                    store.impose(new IfThen(new XeqC(away[w][p], t), new XeqY(opp[t][w], home[w][p])));
                }
            }
            // the n-1 opponents of team t are all different, so t meets every other team once
            store.impose(new Alldistinct(opp[t]));
        }

        // label the home and away teams of every slot, so every choice fixes its slot
        // label the home and away teams of every slot in week order, so every choice fixes its slot
        IntVar[] order = new IntVar[2 * weeks * periods];
        int c = 0;
        for (int w = 0; w < weeks; w++) {
            for (int p = 0; p < periods; p++) {
                order[c++] = home[w][p];
                order[c++] = away[w][p];
            }
        }

        Model m = new Model().put("home", home).put("away", away);
        m.search(order, null, null);
        return m;
    }
}
