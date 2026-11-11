% wolf_goat_cabbage: a MiniZinc model from DCP Rosetta.
%
% The wolf, goat and cabbage problem is a river crossing puzzle. It dates back to at least the 9th
% century, and has entered the folklore of several cultures.
%
% The story: A farmer with a wolf, a goat, and a cabbage must cross a river by boat. The boat can carry
% only the farmer and a single item. If left unattended together, the wolf would eat the goat, or the
% goat would eat the cabbage. How can they cross the river without anything being eaten?
%
% The crossing takes the given number of stages. At the first stage everything is on the starting shore,
% at the last stage everything is on the destination shore, and the boat, with the farmer, changes shore
% from each stage to the next.
%
% Save this file as model.mzn. Download `wolf_goat_cabbage.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py wolf_goat_cabbage.json
%   minizinc model.mzn wolf_goat_cabbage_1.json

int: stage;                           % the number of stages, the first and the last included
set of int: Stages = 1..stage;        % the stages, from the first to the last

% the shore of each item and of the boat at each stage: true for the destination shore, false for the starting shore
array[Stages] of var bool: wolf_pos;
array[Stages] of var bool: goat_pos;
array[Stages] of var bool: cabbage_pos;
array[Stages] of var bool: boat_pos;

% at the first stage everything is on the starting shore
constraint not wolf_pos[1] /\ not goat_pos[1] /\ not cabbage_pos[1] /\ not boat_pos[1];

% at the last stage everything is on the destination shore
constraint wolf_pos[stage] /\ goat_pos[stage] /\ cabbage_pos[stage] /\ boat_pos[stage];

% the boat changes shore from each stage to the next
constraint forall(s in 1..stage - 1)(boat_pos[s] != boat_pos[s + 1]);

% the boat carries the farmer and at most one item, so an item changes shore only from the boat's shore
constraint forall(s in 1..stage - 1)(wolf_pos[s] != wolf_pos[s + 1] -> wolf_pos[s] = boat_pos[s]);
constraint forall(s in 1..stage - 1)(goat_pos[s] != goat_pos[s + 1] -> goat_pos[s] = boat_pos[s]);
constraint forall(s in 1..stage - 1)(cabbage_pos[s] != cabbage_pos[s + 1] -> cabbage_pos[s] = boat_pos[s]);

% the boat carries a single item at most, so at most one item changes shore at each crossing
constraint forall(s in 1..stage - 1)(
    bool2int(wolf_pos[s] != wolf_pos[s + 1]) + bool2int(goat_pos[s] != goat_pos[s + 1])
    + bool2int(cabbage_pos[s] != cabbage_pos[s + 1]) <= 1);

% the wolf is never left alone with the goat: where they share a shore, the farmer is there too
constraint forall(s in Stages)(wolf_pos[s] = goat_pos[s] -> boat_pos[s] = wolf_pos[s]);

% the goat is never left alone with the cabbage: where they share a shore, the farmer is there too
constraint forall(s in Stages)(goat_pos[s] = cabbage_pos[s] -> boat_pos[s] = goat_pos[s]);

solve satisfy;
output ["{\"wolf_pos\": ", showJSON(wolf_pos),
        ", \"goat_pos\": ", showJSON(goat_pos),
        ", \"cabbage_pos\": ", showJSON(cabbage_pos),
        ", \"boat_pos\": ", showJSON(boat_pos), "}"];
