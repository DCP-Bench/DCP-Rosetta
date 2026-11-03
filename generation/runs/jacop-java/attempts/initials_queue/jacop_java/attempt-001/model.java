// Initials queue: ten people in a queue, each with initials that are an alphabetically ordered pair
// of distinct letters from A..E (coded 0..4). Initials are all different, and no two people next to
// each other share a letter. Clues: the front is BE, second is CD, the last is BD.
// Output: queue[i] = [first letter, second letter] of the i-th person from the front.

import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XltY;
import org.jacop.constraints.XneqY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Problem constants: letters A..E are 0..4, and the queue has ten people.
        int numPeople = 10;
        int numLetters = 5;

        // queue[i][0] and queue[i][1] are the letters of person i (0 = A, ..., 4 = E).
        IntVar[][] queue = new IntVar[numPeople][2];
        for (int i = 0; i < numPeople; i++) {
            queue[i][0] = new IntVar(store, "first" + i, 0, numLetters - 1);
            queue[i][1] = new IntVar(store, "second" + i, 0, numLetters - 1);
            // Initials are alphabetically ordered and distinct: first < second.
            store.impose(new XltY(queue[i][0], queue[i][1]));
        }

        // Each pair of initials gets a code 5*first + second, which is unique per pair.
        // All ten codes differ, so no two people have the same initials.
        IntVar[] code = new IntVar[numPeople];
        for (int i = 0; i < numPeople; i++) {
            code[i] = new IntVar(store, "code" + i, 0, 4 * numLetters + numLetters - 1);
            store.impose(new LinearInt(new IntVar[]{queue[i][0], queue[i][1], code[i]},
                    new int[]{5, 1, -1}, "==", 0));
        }
        store.impose(new Alldifferent(code));

        // No one shares a letter with the person in front: the two pairs share no letter.
        for (int i = 0; i + 1 < numPeople; i++) {
            for (int a = 0; a < 2; a++) {
                for (int b = 0; b < 2; b++) {
                    store.impose(new XneqY(queue[i][a], queue[i + 1][b]));
                }
            }
        }

        // Clues from the statement: BE at the front (1, 4), CD right behind (2, 3),
        // BD at the end of the queue (1, 3).
        store.impose(new XeqC(queue[0][0], 1));
        store.impose(new XeqC(queue[0][1], 4));
        store.impose(new XeqC(queue[1][0], 2));
        store.impose(new XeqC(queue[1][1], 3));
        store.impose(new XeqC(queue[numPeople - 1][0], 1));
        store.impose(new XeqC(queue[numPeople - 1][1], 3));

        return new Model().put("queue", queue);
    }
}
