% best_host: a MiniZinc model from DCP Rosetta.
%
% Hosting a dinner party: six guests sit around a table, and some guests do not get along, so two guests
% who do not get along must not sit next to each other. Andrew will only sit next to Dave and Frank;
% Betty will only sit next to Cara and Erica; Cara will only sit next to Betty and Frank; Dave will only
% sit next to Andrew and Erica; Erica will only sit next to Betty and Dave; Frank will only sit next to
% Andrew and Cara. Arrange the guests in a seating order around the table in which every guest sits
% only next to the guests they will sit next to.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: n = 6;                                   % the number of guests, and of seats
int: Andrew = 0;
int: Betty = 1;
int: Cara = 2;
int: Dave = 3;
int: Erica = 4;
int: Frank = 5;

set of int: Guests = 0..n-1;                  % the guests, by number
set of int: Seats = 1..n;                     % the seats around the table, in order

% the ordered pairs of guests who will sit next to each other (each pair listed both ways round)
array[1..12, 1..2] of int: willing = array2d(1..12, 1..2, [
    Andrew, Dave,   Andrew, Frank,  Dave, Andrew,   Frank, Andrew,
    Betty, Cara,    Betty, Erica,   Cara, Betty,    Erica, Betty,
    Cara, Frank,    Frank, Cara,    Dave, Erica,    Erica, Dave
]);

% x[s]: the guest in seat s
array[Seats] of var Guests: x;

% each guest has exactly one seat
constraint all_different(x);

% the guests in neighbouring seats (the last seat is next to the first) will sit next to each other
constraint forall(s in Seats)(table([x[s], x[s mod n + 1]], willing));

solve satisfy;
output ["{\"x\": ", showJSON(x), "}"];
