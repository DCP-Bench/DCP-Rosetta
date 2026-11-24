% huey_dewey_louie: a MiniZinc model from DCP Rosetta.
%
% Huey, Dewey and Louie are being questioned by their uncle, and make these statements:
%   - Huey: Dewey and Louie have an equal share in it; if one is guilty, so is the other.
%   - Dewey: If Huey is guilty, then so am I.
%   - Louie: Dewey and I are not both guilty.
% Their uncle, knowing that they are cub scouts, realises that they cannot tell a lie. Has he got
% sufficient information to decide who (if any) are guilty?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

% each variable is true if that nephew is guilty
var bool: huey;
var bool: dewey;
var bool: louie;

% Huey's statement is true: Dewey and Louie are both guilty or both innocent
constraint dewey <-> louie;

% Dewey's statement is true: if Huey is guilty, then Dewey is guilty
constraint huey -> dewey;

% Louie's statement is true: Dewey and Louie are not both guilty
constraint not (dewey /\ louie);

solve satisfy;

output ["{\"huey\": ", showJSON(huey), ", \"dewey\": ", showJSON(dewey), ", \"louie\": ", showJSON(louie), "}"];
