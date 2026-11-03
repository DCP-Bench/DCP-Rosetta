// Nontransitive dice: five dice (Rock, Paper, Scissors, Lizard, Spock), six faces each,
// face values in 1..12. A die A beats die B when A has a strictly larger face than B in
// more than half of the 36 face pairs, that is in at least 19 pairs. The ten beats
// relations of the game must hold and no others are imposed.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XgtY;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int dieCount = 5;   // Rock, Paper, Scissors, Lizard, Spock
        int faces = 6;      // faces per die
        int maxFace = 12;   // face values are 1..12

        // dice[d][f] = value of face f of die d
        IntVar[][] dice = new IntVar[dieCount][faces];
        IntVar[] order = new IntVar[dieCount * faces];
        for (int d = 0; d < dieCount; d++)
            for (int f = 0; f < faces; f++) {
                dice[d][f] = new IntVar(store, "die" + d + "_face" + f, 1, maxFace);
                order[d * faces + f] = dice[d][f];
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
            IntVar[] wins = new IntVar[faces * faces];   // wins[k] = 1 when this face pair counts
            int[] ones = new int[faces * faces];
            int k = 0;
            for (int i = 0; i < faces; i++)
                for (int j = 0; j < faces; j++) {
                    // Reified: the winner's face i is strictly larger than the loser's face j
                    BooleanVar w = new BooleanVar(store, "win" + rel[0] + "_" + rel[1] + "_" + i + "_" + j);
                    store.impose(new Reified(new XgtY(dice[rel[0]][i], dice[rel[1]][j]), w));
                    wins[k] = w;
                    ones[k] = 1;
                    k++;
                }
            // strictly larger in more than half of the 36 pairs: at least 19
            store.impose(new LinearInt(wins, ones, ">=", 19));
        }

        return new Model().put("dice", dice).search(order, null, null);
    }
}
