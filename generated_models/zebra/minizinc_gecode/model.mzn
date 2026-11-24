% zebra: a MiniZinc model from DCP Rosetta.
%
% The Zebra puzzle (sometimes referred to as Einstein's puzzle) is defined as follows.
% There are five houses in a row, numbered from left to right.
% Each of the five houses is painted a different color, and has one inhabitant.
% The inhabitants are all of different nationalities, own different pets, drink different beverages and
% have different jobs.
% We know that:
%  - colors are yellow, green, red, white, and blue
%  - nations of inhabitants are italy, spain, japan, england, and norway
%  - pets are cat, zebra, bear, snails, and horse
%  - drinks are milk, water, tea, coffee, and juice
%  - jobs are painter, sculptor, diplomat, pianist, and doctor
%  - the painter owns the horse
%  - the diplomat drinks coffee
%  - the one who drinks milk lives in the white house
%  - the Spaniard is a painter
%  - the Englishman lives in the red house
%  - the snails are owned by the sculptor
%  - the green house is immediately on the left of the red one
%  - the Norwegian lives immediately on the right of the blue house
%  - the doctor drinks milk
%  - the diplomat is Japanese
%  - the Norwegian owns the zebra
%  - the green house is next to the white one
%  - the horse is owned by the neighbor of the diplomat
%  - the Italian either lives in the red, white or green house
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: n = 5;                             % the number of houses, and of inhabitants of each kind
set of int: Houses = 0..n - 1;            % the houses, numbered from the left, 0 to 4
set of int: Items = 1..n;                 % the items of each kind, in the order named in the statement

% the house of each item of each kind; the same house number in two arrays is the same house
array[Items] of var Houses: colors;       % yellow, green, red, white, blue
array[Items] of var Houses: nations;      % italy, spain, japan, england, norway
array[Items] of var Houses: jobs;         % painter, sculptor, diplomat, pianist, doctor
array[Items] of var Houses: pets;         % cat, zebra, bear, snails, horse
array[Items] of var Houses: drinks;       % milk, water, tea, coffee, juice

var Houses: yellow = colors[1];
var Houses: green = colors[2];
var Houses: red = colors[3];
var Houses: white = colors[4];
var Houses: blue = colors[5];

var Houses: italy = nations[1];
var Houses: spain = nations[2];
var Houses: japan = nations[3];
var Houses: england = nations[4];
var Houses: norway = nations[5];

var Houses: painter = jobs[1];
var Houses: sculptor = jobs[2];
var Houses: diplomat = jobs[3];
var Houses: pianist = jobs[4];
var Houses: doctor = jobs[5];

var Houses: cat = pets[1];
var Houses: zebra = pets[2];
var Houses: bear = pets[3];
var Houses: snails = pets[4];
var Houses: horse = pets[5];

var Houses: milk = drinks[1];
var Houses: water = drinks[2];
var Houses: tea = drinks[3];
var Houses: coffee = drinks[4];
var Houses: juice = drinks[5];

% the houses have different colors
constraint all_different(colors);

% the inhabitants are of different nationalities
constraint all_different(nations);

% the inhabitants have different jobs
constraint all_different(jobs);

% the inhabitants own different pets
constraint all_different(pets);

% the inhabitants drink different beverages
constraint all_different(drinks);

% the painter owns the horse
constraint painter = horse;

% the diplomat drinks coffee
constraint diplomat = coffee;

% the one who drinks milk lives in the white house
constraint white = milk;

% the Spaniard is a painter
constraint spain = painter;

% the Englishman lives in the red house
constraint england = red;

% the snails are owned by the sculptor
constraint snails = sculptor;

% the green house is immediately on the left of the red one
constraint green + 1 = red;

% the Norwegian lives immediately on the right of the blue house
constraint blue + 1 = norway;

% the doctor drinks milk
constraint doctor = milk;

% the diplomat is Japanese
constraint japan = diplomat;

% the Norwegian owns the zebra
constraint norway = zebra;

% the green house is next to the white one
constraint abs(green - white) = 1;

% the horse is owned by the neighbor of the diplomat
constraint abs(horse - diplomat) = 1;

% the Italian lives in the red, white or green house
constraint italy = red \/ italy = white \/ italy = green;

solve satisfy;
output ["{\"colors\": ", showJSON(colors), ", \"nations\": ", showJSON(nations),
        ", \"jobs\": ", showJSON(jobs), ", \"pets\": ", showJSON(pets),
        ", \"drinks\": ", showJSON(drinks), "}"];
