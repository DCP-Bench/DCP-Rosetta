// Cabling: place the n devices in the n slots of a rack (slots 0..n-1, one device per slot)
// so that the total cable length is minimal. A cable joins two devices and has length equal
// to the distance between their slots. cable_struct lists [device, device, number of cables];
// a device pair with k cables contributes k times its slot distance. final_sum is the total
// cable length, to minimise.
// n, devices and cable_struct come from the instance. cable_struct rows mix strings and
// integers, so each row is read element by element.
import org.jacop.constraints.*;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

import java.util.ArrayList;
import java.util.List;

public class Submission {

    public static Model build(JSONObject inst, Store store) {
        JSONArray devices = inst.getJSONArray("devices");
        JSONArray cables = inst.getJSONArray("cable_struct");
        int n = devices.length();

        // slot[d]: the rack slot of device d. Every device gets its own slot.
        IntVar[] slot = new IntVar[n];
        for (int d = 0; d < n; d++)
            slot[d] = new IntVar(store, "slot_" + devices.getString(d), 0, n - 1);
        store.impose(new Alldistinct(slot));

        // Each cable adds its slot distance. The distance is |slot[a] - slot[b]|. A cable count
        // of k is k copies of the distance in the sum, so the sum needs no weights.
        int maxCost = 0;
        List<IntVar> lengths = new ArrayList<>();
        for (int r = 0; r < cables.length(); r++) {
            JSONArray row = cables.getJSONArray(r);
            int a = indexOf(devices, row.getString(0));
            int b = indexOf(devices, row.getString(1));
            int count = row.getInt(2);

            // diff = slot[a] - slot[b], written as slot[b] + diff == slot[a].
            IntVar diff = new IntVar(store, "diff_" + r, -(n - 1), n - 1);
            store.impose(new XplusYeqZ(slot[b], diff, slot[a]));

            // length = |diff|
            IntVar length = new IntVar(store, "length_" + r, 0, n - 1);
            store.impose(new AbsXeqY(diff, length));

            for (int k = 0; k < count; k++) lengths.add(length);
            maxCost += count * (n - 1);
        }

        // Total cable length: the objective, also the declared output final_sum.
        IntVar total = new IntVar(store, 0, maxCost);
        store.impose(new SumInt(lengths.toArray(new IntVar[0]), "==", total));

        return new Model().put("final_sum", total).minimize(total);
    }

    static int indexOf(JSONArray devices, String name) {
        for (int d = 0; d < devices.length(); d++)
            if (devices.getString(d).equals(name)) return d;
        throw new IllegalArgumentException("unknown device " + name);
    }
}
