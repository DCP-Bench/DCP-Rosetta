// Arch friends: Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats, purple pumps,
// suede sandals) at four stores (Foot Farm, Heels in a Handcart, The Shoe Palace, Tootsies), one pair
// per stop. Stops are numbered 1..4 in the order of the visits. Each shoe and each store takes a
// different stop. Outputs give the stop of each shoe and of each store.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XeqY;
import org.jacop.constraints.XneqY;
import org.jacop.constraints.XplusCeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Stop numbers 1..4 for the shoes.
        IntVar ecru = new IntVar(store, "ecru", 1, 4);
        IntVar fuchsia = new IntVar(store, "fuchsia", 1, 4);
        IntVar purple = new IntVar(store, "purple", 1, 4);
        IntVar suede = new IntVar(store, "suede", 1, 4);

        // Stop numbers 1..4 for the stores.
        IntVar footFarm = new IntVar(store, "footFarm", 1, 4);
        IntVar heels = new IntVar(store, "heels", 1, 4);
        IntVar shoePalace = new IntVar(store, "shoePalace", 1, 4);
        IntVar tootsies = new IntVar(store, "tootsies", 1, 4);

        // Each shoe is bought at a different stop, and each store is a different stop.
        store.impose(new Alldifferent(new IntVar[]{ecru, fuchsia, purple, suede}));
        store.impose(new Alldifferent(new IntVar[]{footFarm, heels, shoePalace, tootsies}));

        // Clue 1: the fuchsia flats were bought at Heels in a Handcart, so the two stops are equal.
        store.impose(new XeqY(fuchsia, heels));

        // Clue 2: the store visited just after the purple pumps was not Tootsies. Tootsies is not
        // at the stop that follows the purple pumps.
        IntVar purpleNext = new IntVar(store, 2, 5);
        store.impose(new XplusCeqZ(purple, 1, purpleNext));
        store.impose(new XneqY(tootsies, purpleNext));

        // Clue 3: the Foot Farm was the second stop.
        store.impose(new XeqC(footFarm, 2));

        // Clue 4: two stops after leaving The Shoe Palace, Harriet bought the suede sandals.
        IntVar shoePalaceLater = new IntVar(store, 3, 6);
        store.impose(new XplusCeqZ(shoePalace, 2, shoePalaceLater));
        store.impose(new XeqY(suede, shoePalaceLater));

        return new Model()
                .put("ecruespadrilles", ecru)
                .put("fuchsiaflats", fuchsia)
                .put("purplepumps", purple)
                .put("suedesandals", suede)
                .put("footfarm", footFarm)
                .put("heelsinahandcart", heels)
                .put("theshoepalace", shoePalace)
                .put("tootsies", tootsies);
    }
}
