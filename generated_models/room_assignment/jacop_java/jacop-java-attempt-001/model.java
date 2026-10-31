// Room assignment: each request (a stay from its start date up to, not including, its end date) is
// given one room out of 0..max_rooms-1. Two requests that overlap in time need different rooms.
// A request with a pre-assigned room (preassigned_room_data >= 0) keeps that room.
import java.time.LocalDate;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XneqY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int rooms = inst.getInt("max_rooms");
        JSONArray startData = inst.getJSONArray("start_data");   // "YYYY-MM-DD" strings
        JSONArray endData = inst.getJSONArray("end_data");       // check-out day, exclusive
        JSONArray pre = inst.getJSONArray("preassigned_room_data");
        int n = startData.length();

        // Dates as day numbers (days since 1970-01-01), so intervals can be compared
        long[] start = new long[n];
        long[] end = new long[n];
        for (int i = 0; i < n; i++) {
            start[i] = LocalDate.parse(startData.getString(i)).toEpochDay();
            end[i] = LocalDate.parse(endData.getString(i)).toEpochDay();
        }

        // room[i] = room of request i, between 0 and max_rooms - 1
        IntVar[] room = new IntVar[n];
        for (int i = 0; i < n; i++)
            room[i] = new IntVar(store, "room" + i, 0, rooms - 1);

        // Pre-assigned rooms: -1 means none
        for (int i = 0; i < n; i++) {
            int r = pre.getInt(i);
            if (r >= 0)
                store.impose(new XeqC(room[i], r));
        }

        // Stays [start, end) overlap when each one starts before the other ends. Overlapping
        // requests must not share a room.
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                if (start[i] < end[j] && start[j] < end[i])
                    store.impose(new XneqY(room[i], room[j]));

        return new Model().put("room_assignments", room);
    }
}
