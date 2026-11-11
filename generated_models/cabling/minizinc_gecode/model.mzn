% cabling: a MiniZinc model from DCP Rosetta.
%
% A rack cabinet holds a number of 1U devices, such as servers and routers, and some devices must be
% connected by several cables. Each device takes one position in the rack, and neighbouring positions
% are one unit apart. A cable between two devices is as long as the distance between their positions,
% so connecting them by k cables costs k times that distance. Place the devices so that the sum of all
% cable lengths is as short as possible.
%
% Save this file as model.mzn. Download `cabling.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py cabling.json
%   minizinc model.mzn cabling_1.json

include "globals.mzn";

int: n;                                  % the number of devices, which is also the number of positions
array[int] of string: devices;           % devices[d]: the name of device d
% The rows of cable_struct are [device, device, number of cables]. The converter binds the two
% name columns and the cable count as separate arrays:
array[int] of string: cable_struct_1;    % cable_struct_1[c]: the first device of cable row c
array[int] of string: cable_struct_2;    % cable_struct_2[c]: the second device of cable row c
array[int] of int: cable_struct_3;       % cable_struct_3[c]: the number of cables in row c

set of int: Devices = index_set(devices);
set of int: Cables = index_set(cable_struct_3);
set of int: Positions = 1..n;

% the index of the device with the given name
function int: device_index(string: name) = sum(d in Devices where devices[d] = name)(d);
array[Cables] of int: end_a = [device_index(cable_struct_1[c]) | c in Cables];
array[Cables] of int: end_b = [device_index(cable_struct_2[c]) | c in Cables];

% x[d]: the rack position of device d
array[Devices] of var Positions: x;

% each position holds one device
constraint all_different(x);

% cable_length[c]: the total length of the cables in row c, each as long as the distance
% between its two devices
array[Cables] of var 0..(n-1)*max(cable_struct_3): cable_length;
constraint forall(c in Cables)(
    cable_length[c] = cable_struct_3[c] * abs(x[end_a[c]] - x[end_b[c]])
);

% final_sum: the sum of all cable lengths
var 0..(n-1)*sum(cable_struct_3): final_sum = sum(c in Cables)(cable_length[c]);
var int: objective = final_sum;

solve minimize objective;

output ["{\"final_sum\": ", showJSON(final_sum), "}"];
