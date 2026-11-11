% csplib_016_traffic_lights: a MiniZinc model from DCP Rosetta.
%
% Imagine a four-way traffic junction with eight traffic lights. Four lights (V1 to V4) are for
% vehicles, and four (P1 to P4) are for pedestrians. The lights have different states. The problem
% lists the combinations of light states (V_i, P_i, V_{i+1}, P_{i+1}) that are safe for intersecting
% roads, for i = 1..4 (with V_5 = V_1 and P_5 = P_1). Every other combination is disallowed to
% prevent accidents. Vehicle light states: 0 = red, 1 = red-yellow, 2 = green, 3 = yellow.
% Pedestrian light states: 0 = red, 1 = green.
%
% Save this file as model.mzn. Download `csplib_016_traffic_lights.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_016_traffic_lights.json
%   minizinc model.mzn csplib_016_traffic_lights_1.json

% allowed_tuples[k, j]: the j-th light state of the k-th safe combination (V_i, P_i, V_{i+1}, P_{i+1})
array[int, 1..4] of int: allowed_tuples;

set of int: Roads = 1..4;                    % the four roads, road 4 is followed by road 1
set of int: VehicleStates = 0..3;            % red, red-yellow, green, yellow
set of int: PedestrianStates = 0..1;         % red, green

array[Roads] of var VehicleStates: vehicle;        % vehicle[i]: state of vehicle light V_i
array[Roads] of var PedestrianStates: pedestrian;  % pedestrian[i]: state of pedestrian light P_i

% the lights of each road and of the next road (road 4 is followed by road 1) show a safe combination
constraint forall(i in Roads)(
    table([vehicle[i], pedestrian[i], vehicle[i mod 4 + 1], pedestrian[i mod 4 + 1]], allowed_tuples));

% the lights in the order V1, V2, V3, V4, P1, P2, P3, P4
array[1..8] of var int: lights = vehicle ++ pedestrian;

solve satisfy;
output ["{\"lights\": ", showJSON(lights), "}"];
