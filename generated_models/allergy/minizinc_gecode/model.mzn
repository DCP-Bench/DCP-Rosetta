% allergy: a MiniZinc model from DCP Rosetta.
%
% Four friends (two women named Debra and Janet, and two men named Hugh and Rick) found that each of them
% is allergic to something different: eggs, mold, nuts and ragweed. We would like to match each one's
% surname (Baxter, Lemon, Malone and Fleet) with his or her allergy.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

% the friends, numbered Debra 0, Janet 1, Hugh 2, Rick 3
set of int: Friends = 0..3;

% each variable is the friend who has that allergy
var Friends: eggs;
var Friends: mold;
var Friends: nuts;
var Friends: ragweed;

% each variable is the friend who has that surname
var Friends: baxter;
var Friends: lemon;
var Friends: malone;
var Friends: fleet;

% each allergy belongs to exactly one friend
constraint all_different([eggs, mold, nuts, ragweed]);

% each surname belongs to exactly one friend
constraint all_different([baxter, lemon, malone, fleet]);

% Rick is not allergic to mold
constraint mold != 3;

% Baxter is allergic to eggs
constraint eggs = baxter;

% Hugh is neither surnamed Lemon nor Fleet
constraint lemon != 2;
constraint fleet != 2;

% Debra is allergic to ragweed
constraint ragweed = 0;

% Janet, who isn't Lemon, is neither allergic to eggs nor to mold
constraint lemon != 1;
constraint eggs != 1;
constraint mold != 1;

solve satisfy;

output ["{\"baxter\": ", showJSON(baxter), ", \"eggs\": ", showJSON(eggs),
        ", \"fleet\": ", showJSON(fleet), ", \"lemon\": ", showJSON(lemon),
        ", \"malone\": ", showJSON(malone), ", \"mold\": ", showJSON(mold),
        ", \"nuts\": ", showJSON(nuts), ", \"ragweed\": ", showJSON(ragweed), "}"];
