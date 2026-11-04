// Zebra puzzle: five houses (0 = leftmost) with a colour, nation, drink, job and pet each.
// Every output gives the house number for each value of its category, in the statement's order.
import org.jacop.constraints.*;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    // Value order from the statement. Each index names one value of its category.
    static final int YELLOW = 0, GREEN = 1, RED = 2, WHITE = 3, BLUE = 4;
    static final int ITALY = 0, SPAIN = 1, JAPAN = 2, ENGLAND = 3, NORWAY = 4;
    static final int CAT = 0, ZEBRA = 1, BEAR = 2, SNAILS = 3, HORSE = 4;
    static final int MILK = 0, WATER = 1, TEA = 2, COFFEE = 3, JUICE = 4;
    static final int PAINTER = 0, SCULPTOR = 1, DIPLOMAT = 2, PIANIST = 3, DOCTOR = 4;

    public static Model build(JSONObject instance, Store store) {
        // colour[c], nation[n], drink[k], job[j], pet[p]: the house (0..4) holding that value.
        IntVar[] colour = houses(store, "colour", 5);
        IntVar[] nation = houses(store, "nation", 5);
        IntVar[] drink = houses(store, "drink", 5);
        IntVar[] job = houses(store, "job", 5);
        IntVar[] pet = houses(store, "pet", 5);

        // Each category fills the five houses, one value each.
        store.impose(new Alldifferent(colour));
        store.impose(new Alldifferent(nation));
        store.impose(new Alldifferent(drink));
        store.impose(new Alldifferent(job));
        store.impose(new Alldifferent(pet));

        // The painter owns the horse.
        store.impose(new XeqY(job[PAINTER], pet[HORSE]));
        // The diplomat drinks coffee.
        store.impose(new XeqY(job[DIPLOMAT], drink[COFFEE]));
        // The one who drinks milk lives in the white house.
        store.impose(new XeqY(drink[MILK], colour[WHITE]));
        // The Spaniard is a painter.
        store.impose(new XeqY(nation[SPAIN], job[PAINTER]));
        // The Englishman lives in the red house.
        store.impose(new XeqY(nation[ENGLAND], colour[RED]));
        // The snails are owned by the sculptor.
        store.impose(new XeqY(pet[SNAILS], job[SCULPTOR]));
        // The green house is immediately on the left of the red one.
        store.impose(new XplusCeqZ(colour[GREEN], 1, colour[RED]));
        // The Norwegian lives immediately on the right of the blue house.
        store.impose(new XplusCeqZ(colour[BLUE], 1, nation[NORWAY]));
        // The doctor drinks milk.
        store.impose(new XeqY(job[DOCTOR], drink[MILK]));
        // The diplomat is Japanese.
        store.impose(new XeqY(job[DIPLOMAT], nation[JAPAN]));
        // The Norwegian owns the zebra.
        store.impose(new XeqY(nation[NORWAY], pet[ZEBRA]));
        // The green house is next to the white one.
        neighbours(store, colour[GREEN], colour[WHITE]);
        // The horse is owned by the neighbour of the diplomat.
        neighbours(store, pet[HORSE], job[DIPLOMAT]);
        // The Italian lives in the red, white or green house.
        anyOf(store, nation[ITALY], colour[RED], colour[WHITE], colour[GREEN]);

        return new Model()
                .put("colors", colour)
                .put("drinks", drink)
                .put("jobs", job)
                .put("nations", nation)
                .put("pets", pet);
    }

    static IntVar[] houses(Store store, String name, int n) {
        IntVar[] h = new IntVar[n];
        for (int i = 0; i < n; i++) h[i] = new IntVar(store, name + i, 0, n - 1);
        return h;
    }

    // a and b are in adjacent houses: |a - b| = 1.
    static void neighbours(Store store, IntVar a, IntVar b) {
        IntVar diff = new IntVar(store, -4, 4);
        IntVar absDiff = new IntVar(store, 0, 4);
        store.impose(new XplusYeqZ(b, diff, a));   // b + diff = a
        store.impose(new AbsXeqY(diff, absDiff));
        store.impose(new XeqC(absDiff, 1));
    }

    // x equals one of the given houses.
    static void anyOf(Store store, IntVar x, IntVar... options) {
        BooleanVar[] hits = new BooleanVar[options.length];
        for (int k = 0; k < options.length; k++) {
            hits[k] = new BooleanVar(store, "hit" + k);
            store.impose(new Reified(new XeqY(x, options[k]), hits[k]));
        }
        store.impose(new LinearInt(hits, ones(options.length), ">=", 1));
    }

    static int[] ones(int n) {
        int[] w = new int[n];
        java.util.Arrays.fill(w, 1);
        return w;
    }
}
