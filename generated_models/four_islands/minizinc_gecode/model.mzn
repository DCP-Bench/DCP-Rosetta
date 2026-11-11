% four_islands: a MiniZinc model from DCP Rosetta.
%
% A tiny nation in the South Pacific contains four islands connected by bridges, laid out as
%     (A) -- (B)
%      |      |
%     (C) -- (D)
% so that A is north of C, C is west of D, and so on. Each of the islands Pwana, Quero, Rayou and
% Skern has a different primary export (alabaster, bananas, coconuts, durian fruit) and a different
% tourist attraction (resort hotel, ice skating rink, jai alai stadium, koala preserve). Find the
% name, export and tourist attraction of each island on the map, from these clues:
%   1. The island noted for its koala preserve is due south of Pwana.
%   2. The island with the largest alabaster quarry is due west of Quero.
%   3. The island with the resort hotel is due east of the one that exports durian fruit.
%   4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
%   5. Rayou and the island that exports bananas are connected by an east-west bridge.
%   6. The islands noted for the South Pacific's largest ice skating rink and for the jai alai
%      stadium are not connected by a bridge.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: A = 0;                       % map positions, as the map is laid out
int: B = 1;
int: C = 2;
int: D = 3;
set of int: Positions = A..D;

% island[i]: map position of the island called Pwana, Quero, Rayou, Skern (i = 1..4)
array[1..4] of var Positions: island;
var Positions: Pwana = island[1];
var Positions: Quero = island[2];
var Positions: Rayou = island[3];
var Positions: Skern = island[4];

% export[i]: map position of the island that exports alabaster, bananas, coconuts, durian fruit
array[1..4] of var Positions: export;
var Positions: alabaster = export[1];
var Positions: bananas = export[2];
var Positions: coconuts = export[3];
var Positions: durian_fruit = export[4];

% attraction[i]: map position of the island with the resort hotel, ice skating rink, jai alai
% stadium, koala preserve
array[1..4] of var Positions: attraction;
var Positions: resort_hotel = attraction[1];
var Positions: ice_skating_rink = attraction[2];
var Positions: jai_alai_stadium = attraction[3];
var Positions: koala_preserve = attraction[4];

% each island has a different name, a different export and a different attraction
constraint all_different(island);
constraint all_different(export);
constraint all_different(attraction);

% the island noted for its koala preserve is due south of Pwana
constraint (Pwana = A /\ koala_preserve = C) \/ (Pwana = B /\ koala_preserve = D);

% the island with the largest alabaster quarry is due west of Quero
constraint (alabaster = A /\ Quero = B) \/ (alabaster = C /\ Quero = D);

% the island with the resort hotel is due east of the one that exports durian fruit
constraint (durian_fruit = A /\ resort_hotel = B) \/ (durian_fruit = C /\ resort_hotel = D);

% Skern and the island with the jai alai stadium are connected by a north-south bridge
constraint (Skern = A /\ jai_alai_stadium = C) \/ (Skern = C /\ jai_alai_stadium = A) \/
           (Skern = B /\ jai_alai_stadium = D) \/ (Skern = D /\ jai_alai_stadium = B);

% Rayou and the island that exports bananas are connected by an east-west bridge
constraint (Rayou = A /\ bananas = B) \/ (Rayou = B /\ bananas = A) \/
           (Rayou = C /\ bananas = D) \/ (Rayou = D /\ bananas = C);

% the islands with the ice skating rink and the jai alai stadium are not connected by a bridge
constraint (ice_skating_rink = A /\ jai_alai_stadium = D) \/ (ice_skating_rink = D /\ jai_alai_stadium = A) \/
           (ice_skating_rink = B /\ jai_alai_stadium = C) \/ (ice_skating_rink = C /\ jai_alai_stadium = B);

solve satisfy;

output ["{\"island\": ", showJSON(island), ", \"export\": ", showJSON(export),
        ", \"attraction\": ", showJSON(attraction), "}"];
