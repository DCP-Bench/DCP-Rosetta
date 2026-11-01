// Nontransitive dice: five dice (Rock, Paper, Scissors, Lizard, Spock), six faces each,
// face values 1..12. Die A beats die B when A shows a strictly larger face in more than half
// of the 36 face pairs, i.e. at least 19. The ten beats relations of the game must hold.
//
// Counting view: for every die, with[v] = number of faces equal to v (GCC) and
// below[v] = number of faces smaller than v. The pairs won by A over B are
// sum over v of with_A[v] * below_B[v], which propagates far better than 36 reified
// comparisons. Faces of each die are kept non-decreasing (dice are multisets, so this only
// removes permutations of the same die).
import org.jacop.constraints.*;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.search.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int dieCount = 5;   // Rock, Paper, Scissors, Lizard, Spock
        int faces = 6;      // faces per die
        int maxFace = 12;   // face values are 1..12

        IntVar[][] dice = new IntVar[dieCount][faces];
        IntVar[][] with = new IntVar[dieCount][maxFace + 1];    // with[d][v]: faces of die d equal to v
        IntVar[][] below = new IntVar[dieCount][maxFace + 1];   // below[d][v]: faces of die d below v
        java.util.List<IntVar> cl = new java.util.ArrayList<>();

        for (int d = 0; d < dieCount; d++) {
            for (int f = 0; f < faces; f++) {
                dice[d][f] = new IntVar(store, "die" + d + "_face" + f, 1, maxFace);
                if (f > 0) store.impose(new XlteqY(dice[d][f - 1], dice[d][f]));
            }
            // GCC counts the values 0, 1, ...: count the shifted faces face-1 in 0..11
            IntVar[] shifted = new IntVar[faces];
            for (int f = 0; f < faces; f++) {
                shifted[f] = new IntVar(store, "shift" + d + "_" + f, 0, maxFace - 1);
                store.impose(new XplusCeqZ(shifted[f], 1, dice[d][f]));
            }
            IntVar[] cnt = new IntVar[maxFace];
            for (int v = 1; v <= maxFace; v++) {
                cnt[v - 1] = new IntVar(store, "with" + d + "_" + v, 0, faces);
                with[d][v] = cnt[v - 1];
            }
            store.impose(new GCC(shifted, cnt));
            below[d][0] = new IntVar(store, "below" + d + "_0", 0, 0);
            below[d][1] = new IntVar(store, "below" + d + "_1", 0, 0);
            for (int v = 2; v <= maxFace; v++) {
                below[d][v] = new IntVar(store, "below" + d + "_" + v, 0, faces);
                store.impose(new XplusYeqZ(below[d][v - 1], with[d][v - 1], below[d][v]));
            }
        }

        // The ten beats relations, as {winner, loser}, with 0 Rock, 1 Paper, 2 Scissors,
        // 3 Lizard, 4 Spock:
        // Rock crushes Scissors, Rock crushes Lizard, Paper covers Rock, Paper disproves Spock,
        // Scissors cuts Paper, Scissors decapitates Lizard, Lizard eats Paper,
        // Lizard poisons Spock, Spock vaporizes Rock, Spock smashes Scissors.
        int[][] beats = {
            {0, 2}, {0, 3}, {1, 0}, {1, 4}, {2, 1},
            {2, 3}, {3, 1}, {3, 4}, {4, 0}, {4, 2}
        };
        for (int[] rel : beats) {
            int a = rel[0], b = rel[1];
            IntVar[] prod = new IntVar[maxFace];
            int[] ones = new int[maxFace];
            for (int v = 1; v <= maxFace; v++) {
                prod[v - 1] = new IntVar(store, "p" + a + b + "_" + v, 0, faces * faces);
                store.impose(new XmulYeqZ(with[a][v], below[b][v], prod[v - 1]));
                ones[v - 1] = 1;
            }
            // strictly larger in more than half of the 36 pairs: at least 19
            store.impose(new LinearInt(prod, ones, ">=", 19));
        }

        // Search: label the face counts die by die in the order Rock, Scissors, Paper, Lizard,
        // Spock (so that each new die closes a beats relation with the dice already fixed),
        // input order, middle value first. Random value order solved it only on some runs.
        for (int d : new int[]{0, 2, 1, 3, 4}) for (int v = 1; v <= maxFace; v++) cl.add(with[d][v]);
        return new Model().put("dice", dice).search(cl.toArray(new IntVar[0]), null, new IndomainMiddle<IntVar>());
    }
}
