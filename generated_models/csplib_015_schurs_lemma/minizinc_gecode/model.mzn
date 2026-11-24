% csplib_015_schurs_lemma: a MiniZinc model from DCP Rosetta.
%
% Put n balls labelled 1, ..., n into c boxes so that for any triple of balls (x, y, z) with
% x + y = z, where x and y may be equal, not all three are in the same box.
%
% Save this file as model.mzn. Download `csplib_015_schurs_lemma.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_015_schurs_lemma.json
%   minizinc model.mzn csplib_015_schurs_lemma_1.json

int: n;                                      % the number of balls
int: c;                                      % the number of boxes

set of int: Balls = 1..n;                    % the balls, labelled from 1
set of int: Boxes = 1..c;                    % the boxes, numbered from 1

% balls[i]: the box ball i is in
array[Balls] of var Boxes: balls;

% for each triple of balls x, y, z = x + y (x and y may be equal), not all three are in the same box
constraint forall(x in Balls, y in x..n where x + y <= n)(
    not (balls[x] = balls[y] /\ balls[y] = balls[x + y]));

solve satisfy;
output ["{\"balls\": ", showJSON(balls), "}"];
