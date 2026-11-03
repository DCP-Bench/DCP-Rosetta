// Sports tournament scheduling: n teams play over n-1 weeks. Each week is split into n/2
// periods, and each period into a home slot and an away slot. Teams are numbered 1..n.
// home[w][p] and away[w][p] are the teams in the two slots of period p in week w.
// The tournament must satisfy three constraints:
//   1. every team plays once a week;
//   2. every team plays at most twice in the same period over the tournament;
//   3. every team plays every other team (exactly once: there are as many games as pairs).
//
// Two symmetry rules, valid because no constraint depends on which team is home or on the team labels:
// home < away in every game, and week 1 is (1,2), (3,4), ... (relabel the teams).
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n_teams");
        int weeks = n - 1;
        int periods = n / 2;

        IntVar[][] home = new IntVar[weeks][periods];
        IntVar[][] away = new IntVar[weeks][periods];
        // opp[w][t-1] is the opponent of team t in week w; the list index of Element is the team (1-based).
        IntVar[][] opp = new IntVar[weeks][n];
        for (int w = 0; w < weeks; w++) {
            for (int t = 1; t <= n; t++) {
                opp[w][t - 1] = new IntVar(store, "opp" + w + "_" + t, 1, n);
                store.impose(new XneqC(opp[w][t - 1], t));
            }
            for (int p = 0; p < periods; p++) {
                home[w][p] = new IntVar(store, "home" + w + "_" + p, 1, n);
                away[w][p] = new IntVar(store, "away" + w + "_" + p, 1, n);
                store.impose(new XltY(home[w][p], away[w][p]));
            }
        }

        // Week 1 fixed by relabelling the teams.
        for (int p = 0; p < periods; p++) {
            store.impose(new XeqC(home[0][p], 2 * p + 1));
            store.impose(new XeqC(away[0][p], 2 * p + 2));
        }

        // 1. Every team plays once a week: the opponent array is an involution tied to the slots.
        for (int w = 0; w < weeks; w++) {
            IntVar[] week = new IntVar[n];
            for (int p = 0; p < periods; p++) {
                week[2 * p] = home[w][p];
                week[2 * p + 1] = away[w][p];
                // opp of the home team is the away team, and conversely (offset 0: teams are 1-based indices)
                store.impose(Element.choose(home[w][p], opp[w], away[w][p], 0));
                store.impose(Element.choose(away[w][p], opp[w], home[w][p], 0));
            }
            store.impose(new Alldifferent(week));
        }

        // 3. Every team meets every other team once: its opponents over the weeks are all different.
        for (int t = 0; t < n; t++) {
            IntVar[] col = new IntVar[weeks];
            for (int w = 0; w < weeks; w++) col[w] = opp[w][t];
            store.impose(new Alldifferent(col));
        }

        // 2. Each team appears at most twice in the same period over the tournament. The counter is a
        // fresh variable, not a member of the list.
        for (int p = 0; p < periods; p++) {
            IntVar[] inPeriod = new IntVar[2 * weeks];
            for (int w = 0; w < weeks; w++) {
                inPeriod[2 * w] = home[w][p];
                inPeriod[2 * w + 1] = away[w][p];
            }
            for (int t = 1; t <= n; t++) {
                IntVar times = new IntVar(store, "times" + p + "_" + t, 0, 2);
                store.impose(new Count(inPeriod, times, t));
            }
        }

        // Search: the slots week by week, input order, lowest value first.
        IntVar[] order = new IntVar[2 * weeks * periods];
        int c = 0;
        for (int w = 0; w < weeks; w++)
            for (int p = 0; p < periods; p++) {
                order[c++] = home[w][p];
                order[c++] = away[w][p];
            }

        return new Model().put("home", home).put("away", away).search(order, null, null);
    }
}
