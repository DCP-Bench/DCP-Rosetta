% circular_table_averbach_1_2: a MiniZinc model from DCP Rosetta.
%
% Three players (X, Y, Z) of different nationalities (American, English, French) are seated around a
% circular table playing a game of Hearts. Each passed three cards to the person on their right. Y passed
% three hearts to the American, and X passed the queen of spades and two diamonds to the person who passed
% their cards to the Frenchwoman. Determine the nationality of each person.
%
% Seats are numbered 0, 1, 2, and seat 1 is right of seat 0, seat 2 right of seat 1, and seat 0 right of
% seat 2. Each variable holds the seat of the person it names, so the same value on a person and on a
% nationality means that person has that nationality.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

set of int: Seats = 0..2;

% the seat of each player
var Seats: x;
var Seats: y;
var Seats: z;

% the seat of each nationality
var Seats: american;
var Seats: english;
var Seats: french;

% the three players sit in different seats
constraint all_different([x, y, z]);

% the three nationalities are in different seats
constraint all_different([american, english, french]);

% Y passed to the person on Y's right, who is the American
constraint american = (y + 1) mod 3;

% X passed to the person on X's right, who passed to the Frenchwoman
constraint french = (x + 2) mod 3;

solve satisfy;

output ["{\"x\": ", showJSON(x), ", \"y\": ", showJSON(y), ", \"z\": ", showJSON(z),
        ", \"american\": ", showJSON(american), ", \"english\": ", showJSON(english),
        ", \"french\": ", showJSON(french), "}"];
