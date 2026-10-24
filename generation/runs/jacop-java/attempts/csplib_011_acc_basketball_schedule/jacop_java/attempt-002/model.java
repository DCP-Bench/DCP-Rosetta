// ACC basketball: a double round-robin timetable for n_teams teams over n_days dates, with the
// home/away/bye, weekend, rival and opponent-sequence rules of the statement.
// config[d][i] is the opponent of team i on date d (i itself for a bye).
// where[d][i] is 0 for home, 1 for a bye, 2 for away.
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.jacop.constraints.*;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.search.IndomainMin;
import org.jacop.search.SmallestDomain;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    // Team indices, in the order the statement lists the teams. Problem constants, not instance data.
    static final int CLEM = 0, DUKE = 1, FSU = 2, GT = 3, UMD = 4, UNC = 5, NCST = 6, UVA = 7, WAKE = 8;

    // Rival of each team (-1 for FSU, which has none): Duke-UNC, Clem-GT, NCSt-Wake, UMD-UVA.
    static final int[] RIVAL = {GT, UNC, -1, CLEM, UVA, DUKE, WAKE, UMD, NCST};

    // Mirroring scheme of the statement, with the 1-based dates converted to 0-based.
    static final int[][] MIRROR = {{0, 7}, {1, 8}, {2, 11}, {3, 12}, {4, 13}, {5, 14}, {6, 15}, {9, 16}, {10, 17}};

    // Sum of the given 0/1 variables, relation rel to c.
    static void sum(Store s, List<IntVar> xs, String rel, int c) {
        int[] ws = new int[xs.size()];
        Arrays.fill(ws, 1);
        s.impose(new LinearInt(xs.toArray(new IntVar[0]), ws, rel, c));
    }

    // Weighted sum of the given variables, relation rel to c.
    static void lin(Store s, List<IntVar> xs, int[] ws, String rel, int c) {
        s.impose(new LinearInt(xs.toArray(new IntVar[0]), ws, rel, c));
    }

    public static Model build(JSONObject instance, Store store) {
        int D = instance.getInt("n_days");     // dates
        int T = instance.getInt("n_teams");    // teams
        int last = D - 1;

        // Decision variables.
        IntVar[][] config = new IntVar[D][T];
        IntVar[][] where = new IntVar[D][T];
        for (int d = 0; d < D; d++)
            for (int i = 0; i < T; i++) {
                config[d][i] = new IntVar(store, "config" + d + "_" + i, 0, T - 1);
                where[d][i] = new IntVar(store, "where" + d + "_" + i, 0, 2);
            }

        // Booleans that describe the decisions.
        // H, A, B: team i is at home, away, or on a bye on date d.
        // R[d][i][j]: team i plays team j on date d (i == j is a bye).
        // HM[d][i][j]: team i plays team j at home on date d.
        BooleanVar[][] H = new BooleanVar[D][T], A = new BooleanVar[D][T], B = new BooleanVar[D][T];
        BooleanVar[][][] R = new BooleanVar[D][T][T];
        BooleanVar[][][] HM = new BooleanVar[D][T][T];
        for (int d = 0; d < D; d++)
            for (int i = 0; i < T; i++) {
                H[d][i] = new BooleanVar(store, "H" + d + "_" + i);
                A[d][i] = new BooleanVar(store, "A" + d + "_" + i);
                B[d][i] = new BooleanVar(store, "B" + d + "_" + i);
                store.impose(new Reified(new XeqC(where[d][i], 0), H[d][i]));
                store.impose(new Reified(new XeqC(where[d][i], 2), A[d][i]));
                store.impose(new Reified(new XeqC(where[d][i], 1), B[d][i]));
                for (int j = 0; j < T; j++) {
                    R[d][i][j] = new BooleanVar(store, "R" + d + "_" + i + "_" + j);
                    store.impose(new Reified(new XeqC(config[d][i], j), R[d][i][j]));
                }
            }

        // Channelling. A game is the same game for both teams. A bye is opponent == self. The
        // team at home and the team away are opposite sides of the same game.
        for (int d = 0; d < D; d++)
            for (int i = 0; i < T; i++) {
                store.impose(new XeqY(R[d][i][i], B[d][i]));
                for (int j = 0; j < T; j++) {
                    if (i == j) continue;
                    if (i < j) store.impose(new XeqY(R[d][i][j], R[d][j][i]));
                    HM[d][i][j] = new BooleanVar(store, "HM" + d + "_" + i + "_" + j);
                    // HM = R[i][j] and H[i]
                    lin(store, List.of(HM[d][i][j], R[d][i][j]), new int[]{1, -1}, "<=", 0);
                    lin(store, List.of(HM[d][i][j], H[d][i]), new int[]{1, -1}, "<=", 0);
                    lin(store, List.of(R[d][i][j], H[d][i], HM[d][i][j]), new int[]{1, 1, -1}, "<=", 1);
                    // i plays j at home, so j is away; i plays j away, so j is at home.
                    lin(store, List.of(R[d][i][j], H[d][i], A[d][j]), new int[]{1, 1, -1}, "<=", 1);
                    lin(store, List.of(R[d][i][j], A[d][i], H[d][j]), new int[]{1, 1, -1}, "<=", 1);
                }
            }

        // Double round-robin: each pair meets twice, once at each team's home.
        for (int i = 0; i < T; i++)
            for (int j = 0; j < T; j++) {
                if (i == j) continue;
                List<IntVar> home = new ArrayList<>();
                for (int d = 0; d < D; d++) home.add(HM[d][i][j]);
                sum(store, home, "==", 1);
            }
        for (int i = 0; i < T; i++)
            for (int j = i + 1; j < T; j++) {
                List<IntVar> meet = new ArrayList<>();
                for (int d = 0; d < D; d++) meet.add(R[d][i][j]);
                sum(store, meet, "==", 2);
            }

        // 1. Mirroring: each team meets the same opponent (or has a bye) on both dates of a pair.
        for (int[] pair : MIRROR)
            for (int i = 0; i < T; i++)
                store.impose(new XeqY(config[pair[0]][i], config[pair[1]][i]));

        // 2. No two final aways: no team is away on both of the last two dates.
        for (int i = 0; i < T; i++)
            sum(store, List.of(A[last - 1][i], A[last][i]), "<=", 1);

        // 3. Home/away/bye runs, counted over consecutive dates.
        for (int i = 0; i < T; i++) {
            for (int d = 0; d + 2 < D; d++) {
                // at most two away in a row, at most two home in a row
                sum(store, List.of(A[d][i], A[d + 1][i], A[d + 2][i]), "<=", 2);
                sum(store, List.of(H[d][i], H[d + 1][i], H[d + 2][i]), "<=", 2);
            }
            for (int d = 0; d + 3 < D; d++) {
                // at most three away-or-bye in a row
                List<IntVar> xs = new ArrayList<>();
                for (int k = 0; k < 4; k++) { xs.add(A[d + k][i]); xs.add(B[d + k][i]); }
                sum(store, xs, "<=", 3);
            }
            for (int d = 0; d + 4 < D; d++) {
                // at most four home-or-bye in a row
                List<IntVar> xs = new ArrayList<>();
                for (int k = 0; k < 5; k++) { xs.add(H[d + k][i]); xs.add(B[d + k][i]); }
                sum(store, xs, "<=", 4);
            }
        }

        // 4. Weekend pattern. Weekends are the even-numbered dates, which are the odd 0-based indices.
        // Over the weekends each team has four home games, four away games and one bye.
        for (int i = 0; i < T; i++) {
            List<IntVar> home = new ArrayList<>(), away = new ArrayList<>(), bye = new ArrayList<>();
            for (int d = 1; d < D; d += 2) {
                home.add(H[d][i]);
                away.add(A[d][i]);
                bye.add(B[d][i]);
            }
            sum(store, home, "==", 4);
            sum(store, away, "==", 4);
            sum(store, bye, "==", 1);
        }

        // 5. First weekends: home or bye on at least two of the first five weekends (dates 2, 4, 6, 8, 10).
        for (int i = 0; i < T; i++) {
            List<IntVar> xs = new ArrayList<>();
            for (int d = 1; d <= 9; d += 2) {
                xs.add(H[d][i]);
                xs.add(B[d][i]);
            }
            sum(store, xs, ">=", 2);
        }

        // 6. Rival matches: on the last date, every team except FSU plays its rival, or FSU, or has a bye.
        for (int i = 0; i < T; i++) {
            if (i == FSU) continue;
            List<IntVar> xs = List.of(R[last][i][RIVAL[i]], R[last][i][FSU], R[last][i][i]);
            sum(store, xs, ">=", 1);
        }

        // 7. Constrained matches: these pairings occur at least once on dates 11 to 18 (0-based 10..17).
        int[][] constrained = {{WAKE, UNC}, {WAKE, DUKE}, {GT, UNC}, {GT, DUKE}};
        for (int[] pair : constrained) {
            List<IntVar> xs = new ArrayList<>();
            for (int d = 10; d <= last; d++) xs.add(R[d][pair[0]][pair[1]]);
            sum(store, xs, ">=", 1);
        }

        // 8. Opponent sequences.
        // Two consecutive dates away against UNC and Duke (one of each, in either order).
        for (int d = 0; d + 1 < D; d++)
            for (int i = 0; i < T; i++) {
                int[][] orders = {{UNC, DUKE}, {DUKE, UNC}};
                for (int[] o : orders) {
                    if (i == o[0] || i == o[1]) continue;
                    lin(store, List.of(R[d][i][o[0]], A[d][i], R[d + 1][i][o[1]], A[d + 1][i]),
                        new int[]{1, 1, 1, 1}, "<=", 3);
                }
            }
        // Three consecutive dates against UNC, Duke and Wake, in any order (independent of home/away).
        int[] trio = {UNC, DUKE, WAKE};
        int[][] perms = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
        for (int d = 0; d + 2 < D; d++)
            for (int i = 0; i < T; i++)
                for (int[] p : perms) {
                    int a = trio[p[0]], b = trio[p[1]], c = trio[p[2]];
                    if (i == a || i == b || i == c) continue;
                    sum(store, List.of(R[d][i][a], R[d + 1][i][b], R[d + 2][i][c]), "<=", 2);
                }

        // 9. Other constraints (0-based dates: date k is index k-1).
        store.impose(new XeqC(R[last][UNC][DUKE], 1));      // UNC plays Duke on the last date
        store.impose(new XeqC(R[10][UNC][DUKE], 1));        // ... and on date 11
        store.impose(new XeqC(R[1][UNC][CLEM], 1));         // UNC plays Clem on date 2
        store.impose(new XeqC(B[15][DUKE], 1));             // Duke has a bye on date 16
        store.impose(new XneqC(where[16][WAKE], 0));        // Wake does not play home on date 17
        store.impose(new XeqC(where[0][WAKE], 1));          // Wake has a bye on the first date
        for (int t : new int[]{CLEM, DUKE, UMD, WAKE})      // no away game on the last date
            store.impose(new XneqC(where[last][t], 2));
        for (int t : new int[]{CLEM, FSU, GT, WAKE})        // no away game on the first date
            store.impose(new XneqC(where[0][t], 2));
        for (int t : new int[]{FSU, NCST})                  // no bye on the last date
            store.impose(new XneqC(where[last][t], 1));
        store.impose(new XneqC(where[0][UNC], 1));          // UNC has no bye on the first date

        // Output: config and where, as lists of dates, each a list of teams.
        List<IntVar> flat = new ArrayList<>();
        for (int d = 0; d < D; d++)
            for (int i = 0; i < T; i++) {
                flat.add(config[d][i]);
            }
        for (int d = 0; d < D; d++)
            for (int i = 0; i < T; i++) {
                flat.add(where[d][i]);
            }
        // Redundant counts, implied by the rules above, that help propagation: two byes per team
        // (16 games in 18 dates), and one bye on weekdays (the other bye is on a weekend).
        for (int i = 0; i < T; i++) {
            List<IntVar> byes = new ArrayList<>(), weekdayByes = new ArrayList<>();
            for (int d = 0; d < D; d++) {
                byes.add(B[d][i]);
                if (d % 2 == 0) weekdayByes.add(B[d][i]);
            }
            sum(store, byes, "==", 2);
            sum(store, weekdayByes, "==", 1);
        }

        // Label the schedule's mirror-representative dates first, then the rest, each smallest domain
        // first with the lowest value. A mirrored date is fixed by its partner.
        List<IntVar> order = new ArrayList<>();
        boolean[] rep = new boolean[D];
        for (int[] pair : MIRROR) rep[pair[0]] = true;
        for (int d = 0; d < D; d++) if (rep[d]) for (int i = 0; i < T; i++) order.add(config[d][i]);
        for (int d = 0; d < D; d++) if (!rep[d]) for (int i = 0; i < T; i++) order.add(config[d][i]);
        for (int d = 0; d < D; d++) for (int i = 0; i < T; i++) order.add(where[d][i]);

        return new Model().put("config", config).put("where", where)
                .search(order.toArray(new IntVar[0]), new SmallestDomain<>(), new IndomainMin<>());
    }
}
