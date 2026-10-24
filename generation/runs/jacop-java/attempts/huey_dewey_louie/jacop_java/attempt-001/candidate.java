// Huey, Dewey and Louie: each is guilty or not. Each statement is true, since they cannot tell a lie.
// Huey: Dewey and Louie have equal share in it (both guilty or both innocent).
// Dewey: if Huey is guilty, then so am I.
// Louie: Dewey and I are not both guilty.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    public static Model build(JSONObject instance, Store store) {
        // 1 = guilty, 0 = innocent.
        BooleanVar huey = new BooleanVar(store, "huey");
        BooleanVar dewey = new BooleanVar(store, "dewey");
        BooleanVar louie = new BooleanVar(store, "louie");

        // Huey's statement holds: Dewey and Louie are both guilty or both innocent.
        store.impose(new LinearInt(new BooleanVar[]{dewey, louie}, new int[]{1, -1}, "==", 0));
        // Dewey's statement holds: if Huey is guilty, Dewey is guilty (huey <= dewey).
        store.impose(new LinearInt(new BooleanVar[]{huey, dewey}, new int[]{1, -1}, "<=", 0));
        // Louie's statement holds: Dewey and Louie are not both guilty.
        store.impose(new LinearInt(new BooleanVar[]{dewey, louie}, new int[]{1, 1}, "<=", 1));

        return new Model().put("huey", huey).put("dewey", dewey).put("louie", louie);
    }
}
