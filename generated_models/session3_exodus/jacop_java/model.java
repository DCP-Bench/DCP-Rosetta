import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.Element;
import org.jacop.constraints.XltY;
import org.jacop.constraints.XeqY;
import org.jacop.constraints.XplusCeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

// Labels: every output array holds, for each slot, the label 1..5 of the entity in that slot.
// The same label in two arrays names the same family/child. Entities are labelled by child.
//   children[j]  label of child j      (Bernice, Carl, Debby, Sammy, Ted)
//   ages[a]      label in age slot a   (3, 5, 7, 8, 10)
//   countries[c] label in country slot (Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen)
//   stories[s]   label in story slot   (burning bush, captivity, Moses youth, Passover, Ten Commandments)
// ageOfLabel[k] is the age of the entity with label k+1. It is fixed by the ages array:
// ages[a] = label implies ageOfLabel[label - 1] = AGE[a].
public class Submission {
    static final int[] AGE = {3, 5, 7, 8, 10};

    public static Model build(JSONObject instance, Store store) {
        IntVar[] ages = new IntVar[5];
        IntVar[] children = new IntVar[5];
        IntVar[] countries = new IntVar[5];
        IntVar[] stories = new IntVar[5];
        IntVar[] ageOfLabel = new IntVar[5];
        for (int i = 0; i < 5; i++) {
            ages[i] = new IntVar(store, "ages" + i, 1, 5);
            children[i] = new IntVar(store, "children" + i, 1, 5);
            countries[i] = new IntVar(store, "countries" + i, 1, 5);
            stories[i] = new IntVar(store, "stories" + i, 1, 5);
            ageOfLabel[i] = new IntVar(store, "ageOfLabel" + i, 3, 10);
        }

        // Each array is a permutation of the labels.
        store.impose(new Alldifferent(ages));
        store.impose(new Alldifferent(children));
        store.impose(new Alldifferent(countries));
        store.impose(new Alldifferent(stories));

        // Tie the age of each label to its age slot.
        for (int a = 0; a < 5; a++) {
            IntVar ageValue = new IntVar(store, AGE[a], AGE[a]);
            store.impose(Element.choose(ages[a], ageOfLabel, ageValue, 0));
        }

        // Clue 1: Debby's family is from Lithuania (Debby is child 2, Lithuania is country 2).
        store.impose(new XeqY(children[2], countries[2]));

        // Clue 2: the Passover child is two years older than Bernice (child 0, story 3).
        IntVar agePassover = ageOf(store, stories[3], ageOfLabel);
        IntVar ageBernice = ageOf(store, children[0], ageOfLabel);
        store.impose(new XplusCeqZ(ageBernice, 2, agePassover));

        // Clue 3: the Yemen family (country 4) is younger than the Ethiopian family (country 0).
        IntVar ageYemen = ageOf(store, countries[4], ageOfLabel);
        IntVar ageEthiopia = ageOf(store, countries[0], ageOfLabel);
        store.impose(new XltY(ageYemen, ageEthiopia));

        // Clue 4: the Moroccan family (country 3) is three years older than Ted (child 4).
        IntVar ageMorocco = ageOf(store, countries[3], ageOfLabel);
        IntVar ageTed = ageOf(store, children[4], ageOfLabel);
        store.impose(new XplusCeqZ(ageTed, 3, ageMorocco));

        // Clue 5: Sammy (child 3) is three years older than the Moses's youth child (story 2).
        IntVar ageSammy = ageOf(store, children[3], ageOfLabel);
        IntVar ageMoses = ageOf(store, stories[2], ageOfLabel);
        store.impose(new XplusCeqZ(ageMoses, 3, ageSammy));

        IntVar[] decisions = new IntVar[20];
        for (int i = 0; i < 5; i++) {
            decisions[i] = ages[i];
            decisions[5 + i] = children[i];
            decisions[10 + i] = countries[i];
            decisions[15 + i] = stories[i];
        }

        return new Model()
            .put("ages", ages)
            .put("children", children)
            .put("countries", countries)
            .put("stories", stories)
            .search(decisions, null, null);
    }

    // The age of the entity with the given label, as a fresh variable.
    static IntVar ageOf(Store store, IntVar label, IntVar[] ageOfLabel) {
        IntVar age = new IntVar(store, 3, 10);
        store.impose(Element.choose(label, ageOfLabel, age, 0));
        return age;
    }
}
