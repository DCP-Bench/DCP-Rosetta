% frog_circle: a MiniZinc model from DCP Rosetta.
%
% Cards numbered 1 to n are arranged in a circle. A frog jumps on card 1, then jumps 1 place clockwise
% around the circle. From card k, it then jumps directly k places clockwise around the circle, and it
% continues jumping in this way forever. Find an arrangement of the cards that allows the frog to jump
% on every card, starting from card 1.
%
% Save this file as model.mzn. Download `frog_circle.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py frog_circle.json
%   minizinc model.mzn frog_circle_1.json

include "globals.mzn";

int: n;                                          % the number of cards

set of int: Cards = 1..n;                        % card numbers
set of int: Places = 1..n;                       % places around the circle, numbered clockwise
set of int: Jumps = 1..n;                        % the frog's jumps, in order

% x[p]: the card placed at place p of the circle
array[Places] of var Cards: x;

% pos[k]: the place the frog lands on at its k-th jump (the first one is on card 1)
array[Jumps] of var Places: pos;

% each card is placed once in the circle
constraint all_different(x);

% the frog lands on every place once
constraint all_different(pos);

% the frog starts on card 1; placing card 1 at the first place is a symmetry break (it removes the rotations of an arrangement)
constraint pos[1] = 1;
constraint x[1] = 1;

% from the place it is on, the frog jumps as many places clockwise as the card there shows
constraint forall(k in 1..n-1)(
    pos[k+1] = (pos[k] - 1 + x[pos[k]]) mod n + 1);

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
