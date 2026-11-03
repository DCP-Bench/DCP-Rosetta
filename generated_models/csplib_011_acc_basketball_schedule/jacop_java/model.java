// ACC basketball: a double round-robin timetable for n_teams teams over n_days dates.
// config[d][i] is the opponent of team i on date d (i itself for a bye).
// where[d][i] is 0 for home, 1 for a bye, 2 for away.
//
// Model: the mirroring scheme pairs the 18 dates, and a mirrored date repeats the opponent row of its
// partner with the venues swapped (home <-> away, bye stays a bye). So only the first date of each
// pair, 9 rows, carries free variables. Per free date the row is an all-different involution
// (config[config[i]] = i) with opposite venues for the two teams of a game, and a bye exactly when
// config[i] = i. Per team, the 9 free opponents are all different (each opponent once, bye once) and the
// 9 venues must be one of the venue sequences that satisfy the home/away/bye rules, the weekend rules
// and the final-away rule; those sequences are enumerated in Java and posted as a Table.
import java.util.ArrayList;
import java.util.List;
import org.jacop.constraints.*;
import org.jacop.constraints.table.Table;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    // Team indices, in the order the statement lists the teams. Problem constants, not instance data.
    static final int CLEM = 0, DUKE = 1, FSU = 2, GT = 3, UMD = 4, UNC = 5, NCST = 6, UVA = 7, WAKE = 8;

    // Rival of each team (-1 for FSU, which has none): Duke-UNC, Clem-GT, NCSt-Wake, UMD-UVA.
    static final int[] RIVAL = {GT, UNC, -1, CLEM, UVA, DUKE, WAKE, UMD, NCST};

    // Mirroring scheme of the statement, with the 1-based dates converted to 0-based.
    static final int[][] MIRROR = {{0, 7}, {1, 8}, {2, 11}, {3, 12}, {4, 13}, {5, 14}, {6, 15}, {9, 16}, {10, 17}};

    static final int HOME = 0, BYE = 1, AWAY = 2;

    static void sum(Store s, List<IntVar> xs, String rel, int c) {
        int[] ws = new int[xs.size()];
        java.util.Arrays.fill(ws, 1);
        s.impose(new LinearInt(xs.toArray(new IntVar[0]), ws, rel, c));
    }

    // Is this 18-date venue sequence allowed by the venue rules (2, 3, 4, 5)?
    static boolean venueOk(int[] v) {
        int D = v.length;
        // 2. not away on both of the last two dates
        if (v[D - 1] == AWAY && v[D - 2] == AWAY) return false;
        // 3. runs: at most 2 away, at most 2 home, at most 3 away-or-bye, at most 4 home-or-bye
        for (int d = 0; d + 2 < D; d++) {
            if (v[d] == AWAY && v[d + 1] == AWAY && v[d + 2] == AWAY) return false;
            if (v[d] == HOME && v[d + 1] == HOME && v[d + 2] == HOME) return false;
        }
        for (int d = 0; d + 3 < D; d++) {
            boolean all = true;
            for (int k = 0; k < 4; k++) if (v[d + k] == HOME) all = false;
            if (all) return false;
        }
        for (int d = 0; d + 4 < D; d++) {
            boolean all = true;
            for (int k = 0; k < 5; k++) if (v[d + k] == AWAY) all = false;
            if (all) return false;
        }
        // 4. weekends (odd 0-based dates): four home, four away, one bye
        int h = 0, a = 0, b = 0;
        for (int d = 1; d < D; d += 2) {
            if (v[d] == HOME) h++; else if (v[d] == AWAY) a++; else b++;
        }
        if (h != 4 || a != 4 || b != 1) return false;
        // 5. home or bye on at least two of the first five weekends (dates 1, 3, 5, 7, 9)
        int hb = 0;
        for (int d = 1; d <= 9; d += 2) if (v[d] != AWAY) hb++;
        return hb >= 2;
    }

    public static Model build(JSONObject instance, Store store) {
        int D = instance.getInt("n_days");     // dates
        int T = instance.getInt("n_teams");    // teams
        int last = D - 1;
        int F = MIRROR.length;                 // free dates: one per mirror pair

        // Free variables: opponent and venue of every team on the first date of each pair.
        IntVar[][] cr = new IntVar[F][T], wr = new IntVar[F][T];
        for (int k = 0; k < F; k++)
            for (int i = 0; i < T; i++) {
                cr[k][i] = new IntVar(store, "c" + k + "_" + i, 0, T - 1);
                wr[k][i] = new IntVar(store, "w" + k + "_" + i, 0, 2);
            }

        // Expand to all dates through the mirror map.
        IntVar[][] config = new IntVar[D][], where = new IntVar[D][T];
        for (int k = 0; k < F; k++) {
            int d1 = MIRROR[k][0], d2 = MIRROR[k][1];
            config[d1] = cr[k];
            config[d2] = cr[k];
            where[d1] = wr[k];
            for (int i = 0; i < T; i++) {
                where[d2][i] = new IntVar(store, "wm" + k + "_" + i, 0, 2);
                store.impose(new XplusYeqC(wr[k][i], where[d2][i], 2));
            }
        }

        // Per free date: a perfect matching with at most one bye, and venues of the two teams opposite.
        for (int k = 0; k < F; k++) {
            store.impose(new Alldifferent(cr[k]));
            List<IntVar> byes = new ArrayList<>(), homes = new ArrayList<>(), aways = new ArrayList<>();
            for (int i = 0; i < T; i++) {
                // opponent of my opponent is me
                store.impose(Element.choose(cr[k][i], cr[k], new IntVar(store, i, i), -1));
                // my venue plus my opponent's venue is 2 (home+away, or bye+bye)
                IntVar wo = new IntVar(store, "wo" + k + "_" + i, 0, 2);
                store.impose(Element.choose(cr[k][i], wr[k], wo, -1));
                store.impose(new XplusYeqC(wr[k][i], wo, 2));
                // bye <-> opponent is myself
                BooleanVar b = new BooleanVar(store, "bye" + k + "_" + i);
                store.impose(new Reified(new XeqC(cr[k][i], i), b));
                store.impose(new Reified(new XeqC(wr[k][i], BYE), b));
                byes.add(b);
                BooleanVar h = new BooleanVar(store, "home" + k + "_" + i);
                store.impose(new Reified(new XeqC(wr[k][i], HOME), h));
                homes.add(h);
                BooleanVar a = new BooleanVar(store, "away" + k + "_" + i);
                store.impose(new Reified(new XeqC(wr[k][i], AWAY), a));
                aways.add(a);
            }
            sum(store, byes, "==", 1);
            sum(store, homes, "==", (T - 1) / 2);
            sum(store, aways, "==", (T - 1) / 2);
        }

        // Per team: every opponent once, and the bye once, over the free dates.
        for (int i = 0; i < T; i++) {
            IntVar[] col = new IntVar[F];
            for (int k = 0; k < F; k++) col[k] = cr[k][i];
            store.impose(new Alldifferent(col));
        }

        // Per team: the venue sequence over the free dates comes from the allowed set.
        int total = 1;
        for (int k = 0; k < F; k++) total *= 3;
        List<int[]> tuples = new ArrayList<>();
        int[] pat = new int[F], full = new int[D];
        for (int code = 0; code < total; code++) {
            int c = code, byeCount = 0;
            for (int k = 0; k < F; k++) { pat[k] = c % 3; c /= 3; if (pat[k] == BYE) byeCount++; }
            if (byeCount != 1) continue;
            for (int k = 0; k < F; k++) {
                full[MIRROR[k][0]] = pat[k];
                full[MIRROR[k][1]] = 2 - pat[k];
            }
            if (venueOk(full)) tuples.add(pat.clone());
        }
        int[][] allowed = tuples.toArray(new int[0][]);
        for (int i = 0; i < T; i++) {
            IntVar[] seq = new IntVar[F];
            for (int k = 0; k < F; k++) seq[k] = wr[k][i];
            store.impose(new Table(seq, allowed));
        }

        // Booleans over the full 18-date view: opponent is UNC / Duke / Wake, and team is away.
        int[] key = {UNC, DUKE, WAKE};
        BooleanVar[][][] opp = new BooleanVar[D][T][3];
        BooleanVar[][] away = new BooleanVar[D][T];
        for (int d = 0; d < D; d++)
            for (int i = 0; i < T; i++) {
                for (int q = 0; q < 3; q++) {
                    opp[d][i][q] = new BooleanVar(store, "opp" + d + "_" + i + "_" + q);
                    store.impose(new Reified(new XeqC(config[d][i], key[q]), opp[d][i][q]));
                }
                away[d][i] = new BooleanVar(store, "aw" + d + "_" + i);
                store.impose(new Reified(new XeqC(where[d][i], AWAY), away[d][i]));
            }

        // 6. Rival matches: on the last date every team except FSU plays its rival, plays FSU, or has a bye.
        for (int i = 0; i < T; i++) {
            if (i == FSU) continue;
            List<IntVar> xs = new ArrayList<>();
            int[] vals = {RIVAL[i], FSU, i};
            for (int v : vals) {
                BooleanVar r = new BooleanVar(store, "riv" + i + "_" + v);
                store.impose(new Reified(new XeqC(config[last][i], v), r));
                xs.add(r);
            }
            sum(store, xs, ">=", 1);
        }

        // 7. Constrained matches: these pairings occur at least once on dates 11 to 18 (0-based 10..17).
        int[][] constrained = {{WAKE, UNC}, {WAKE, DUKE}, {GT, UNC}, {GT, DUKE}};
        for (int[] pair : constrained) {
            List<IntVar> xs = new ArrayList<>();
            for (int d = 10; d <= last; d++) {
                BooleanVar r = new BooleanVar(store, "cm" + pair[0] + "_" + pair[1] + "_" + d);
                store.impose(new Reified(new XeqC(config[d][pair[0]], pair[1]), r));
                xs.add(r);
            }
            sum(store, xs, ">=", 1);
        }

        // 8. Opponent sequences.
        // Not away against UNC and then away against Duke on consecutive dates, nor Duke then UNC.
        for (int d = 0; d + 1 < D; d++)
            for (int i = 0; i < T; i++) {
                if (i == UNC || i == DUKE) continue;
                int[][] orders = {{0, 1}, {1, 0}};
                for (int[] o : orders)
                    sum(store, List.of(opp[d][i][o[0]], away[d][i], opp[d + 1][i][o[1]], away[d + 1][i]), "<=", 3);
            }
        // Not UNC, Duke and Wake on three consecutive dates, in any order (home or away).
        int[][] perms = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
        for (int d = 0; d + 2 < D; d++)
            for (int i = 0; i < T; i++) {
                if (i == UNC || i == DUKE || i == WAKE) continue;
                for (int[] p : perms)
                    sum(store, List.of(opp[d][i][p[0]], opp[d + 1][i][p[1]], opp[d + 2][i][p[2]]), "<=", 2);
            }

        // 9. Other constraints (0-based dates: date k is index k-1).
        store.impose(new XeqC(config[last][UNC], DUKE));    // UNC plays Duke on the last date
        store.impose(new XeqC(config[10][UNC], DUKE));      // ... and on date 11
        store.impose(new XeqC(config[1][UNC], CLEM));       // UNC plays Clem on date 2
        store.impose(new XeqC(where[15][DUKE], BYE));       // Duke has a bye on date 16
        store.impose(new XneqC(where[16][WAKE], HOME));     // Wake does not play home on date 17
        store.impose(new XeqC(where[0][WAKE], BYE));        // Wake has a bye on the first date
        for (int t : new int[]{CLEM, DUKE, UMD, WAKE})      // no away game on the last date
            store.impose(new XneqC(where[last][t], AWAY));
        for (int t : new int[]{CLEM, FSU, GT, WAKE})        // no away game on the first date
            store.impose(new XneqC(where[0][t], AWAY));
        for (int t : new int[]{FSU, NCST})                  // no bye on the last date
            store.impose(new XneqC(where[last][t], BYE));
        store.impose(new XneqC(where[0][UNC], BYE));        // UNC has no bye on the first date

        // Search: venues team by team over the free dates, then the opponent rows date by date.
        List<IntVar> order = new ArrayList<>();
        for (int i = 0; i < T; i++) for (int k = 0; k < F; k++) order.add(wr[k][i]);
        for (int k = 0; k < F; k++) for (int i = 0; i < T; i++) order.add(cr[k][i]);

        return new Model().put("config", config).put("where", where)
                .search(order.toArray(new IntVar[0]), null, null);
    }
}
