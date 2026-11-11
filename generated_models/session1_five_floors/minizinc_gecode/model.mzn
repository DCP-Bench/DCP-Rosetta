% session1_five_floors: a MiniZinc model from DCP Rosetta.
%
% Baker, Cooper, Fletcher, Miller, and Smith live on the first five floors of an apartment house. Baker does not
% live on the fifth floor. Cooper does not live on the first floor. Fletcher does not live on either the fifth or the
% first floor. Miller lives on a higher floor than does Cooper. Smith does not live on a floor adjacent to Fletcher's.
% Fletcher does not live on a floor adjacent to Cooper's. They all live on different floors. Find the floors where
% these people live.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

var 1..5: B;   % the floor Baker lives on
var 1..5: C;   % the floor Cooper lives on
var 1..5: F;   % the floor Fletcher lives on
var 1..5: M;   % the floor Miller lives on
var 1..5: S;   % the floor Smith lives on

% they all live on different floors
constraint all_different([B, C, F, M, S]);

% Baker does not live on the fifth floor
constraint B != 5;

% Cooper does not live on the first floor
constraint C != 1;

% Fletcher does not live on either the fifth or the first floor
constraint F != 1 /\ F != 5;

% Miller lives on a higher floor than does Cooper
constraint M > C;

% Smith does not live on a floor adjacent to Fletcher's
constraint abs(S - F) != 1;

% Fletcher does not live on a floor adjacent to Cooper's
constraint abs(F - C) != 1;

solve satisfy;
output ["{\"B\": ", showJSON(B), ", \"C\": ", showJSON(C), ", \"F\": ", showJSON(F), ", \"M\": ", showJSON(M),
        ", \"S\": ", showJSON(S), "}"];
