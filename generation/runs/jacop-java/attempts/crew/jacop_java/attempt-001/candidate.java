// Crew scheduling. Assign each attendant to flights so that every flight gets its
// crew. Instance fields:
//   attributes[p] = [steward, hostess, French, Spanish, German] (0/1 per attendant)
//   required_crew[f] = [crew size, stewards, hostesses, French, Spanish, German]
// Flight f has exactly crew size attendants, and at least the required number of
// stewards, hostesses and speakers of each language. An attendant who works a
// flight has the two following flights off: if attendant p works flight f, then
// p does not work flight f+1 or f+2.
// Output crew[f][p] = 1 when attendant p works flight f.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray attributes = inst.getJSONArray("attributes");
        JSONArray required = inst.getJSONArray("required_crew");
        int people = attributes.length();
        int flights = required.length();

        // crew[f][p] = 1 when attendant p is assigned to flight f
        BooleanVar[][] crew = new BooleanVar[flights][people];
        for (int f = 0; f < flights; f++) {
            for (int p = 0; p < people; p++) {
                crew[f][p] = new BooleanVar(store, "crew" + f + "_" + p);
            }
        }

        for (int f = 0; f < flights; f++) {
            JSONArray req = required.getJSONArray(f);
            IntVar[] onFlight = crew[f];
            int[] ones = new int[people];
            java.util.Arrays.fill(ones, 1);

            // the flight has exactly its crew size
            store.impose(new LinearInt(onFlight, ones, "==", req.getInt(0)));

            // at least the required stewards, hostesses and speakers of each language
            for (int k = 1; k < 6; k++) {
                int[] attr = new int[people];
                for (int p = 0; p < people; p++) {
                    attr[p] = attributes.getJSONArray(p).getInt(k - 1);
                }
                store.impose(new LinearInt(onFlight, attr, ">=", req.getInt(k)));
            }
        }

        // rest rule: after flight f, the next two flights are off for that attendant
        for (int p = 0; p < people; p++) {
            for (int f = 0; f < flights; f++) {
                for (int g = f + 1; g <= f + 2 && g < flights; g++) {
                    store.impose(new LinearInt(
                            new IntVar[]{crew[f][p], crew[g][p]},
                            new int[]{1, 1}, "<=", 1));
                }
            }
        }

        return new Model().put("crew", crew);
    }
}
