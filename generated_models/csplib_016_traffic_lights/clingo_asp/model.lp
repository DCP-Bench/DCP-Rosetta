% csplib_016_traffic_lights: a clingo model from DCP Rosetta.
%
% Imagine a four-way traffic junction with eight traffic lights. Four lights (V1 to V4) are for vehicles, and four (P1
% to P4) are for pedestrians. The lights have different states. The problem lists the combinations of light states
% (V_i, P_i, V_(i+1), P_(i+1)) that are safe for intersecting roads, for i = 1 to 4 (with V_5 = V_1 and P_5 = P_1);
% every other combination is disallowed to prevent accidents. Find a valid state of the eight lights, in the order
% V1, V2, V3, V4, P1, P2, P3, P4.
%
% Vehicle light states: 0 = red, 1 = red-yellow, 2 = green, 3 = yellow. Pedestrian light states: 0 = red, 1 = green.
%
% Save this file as model.lp. Download `csplib_016_traffic_lights.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_016_traffic_lights.json
%   python -m clingo model.lp csplib_016_traffic_lights_1.lp
%
% Input: allowed_tuples(T,J,V): the V of the T-th safe combination in position J, the positions being V_i, P_i,
% V_(i+1), P_(i+1) (indices are 0-based, as in the data).

vehicle_light(0..3).
pedestrian_light(0..3).
vehicle_state(0..3).
pedestrian_state(0..1).

% the safe combinations, each as (vehicle, pedestrian, next vehicle, next pedestrian)
safe(A,B,C,D) :- allowed_tuples(T,0,A), allowed_tuples(T,1,B), allowed_tuples(T,2,C), allowed_tuples(T,3,D).

% vehicle(I,S): vehicle light I has state S; pedestrian(I,S): pedestrian light I has state S
1 { vehicle(I,S) : vehicle_state(S) } 1 :- vehicle_light(I).
1 { pedestrian(I,S) : pedestrian_state(S) } 1 :- pedestrian_light(I).

% next(I,J): the road after road I is road J, the last road being followed by the first
next(I,(I+1) \ 4) :- vehicle_light(I).

% the states of each pair of roads, with the next road, form a safe combination
:- next(I,J), vehicle(I,A), pedestrian(I,B), vehicle(J,C), pedestrian(J,D), not safe(A,B,C,D).

% lights(I,S): light I of the order V1 to V4, P1 to P4 has state S
lights(I,S) :- vehicle(I,S).
lights(4+I,S) :- pedestrian(I,S).

#show lights/2.
