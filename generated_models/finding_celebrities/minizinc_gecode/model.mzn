% finding_celebrities: a MiniZinc model from DCP Rosetta.
%
% Given a list of people at a party and for each person the list of people they know at the party,
% we want to find the celebrities at the party. A celebrity is a person that everybody at the party
% knows but that only knows other celebrities. At least one celebrity is present at the party.
%
% Save this file as model.mzn. Download `finding_celebrities.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py finding_celebrities.json
%   minizinc model.mzn finding_celebrities_1.json

array[int, int] of int: graph;               % graph[i, j] = 1 if person i knows person j
set of int: People = index_set_1of2(graph);  % one index per person

% celebrities[i]: person i is a celebrity
array[People] of var bool: celebrities;

% a celebrity is known by everybody at the party, and knows only other celebrities
constraint forall(i in People)(
    celebrities[i] <-> (forall(j in People)(graph[j, i] = 1)
                        /\ forall(j in People)(graph[i, j] = 1 -> celebrities[j])));
% at least one celebrity is present at the party
constraint exists(i in People)(celebrities[i]);

solve satisfy;
output ["{\"celebrities\": ", showJSON(celebrities), "}"];
