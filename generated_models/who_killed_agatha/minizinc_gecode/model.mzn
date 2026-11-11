% who_killed_agatha: a MiniZinc model from DCP Rosetta.
%
% Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler, and Charles live in Dreadsbury
% Mansion, and are the only ones to live there. A killer always hates, and is no richer than his victim.
% Charles hates noone that Agatha hates. Agatha hates everybody except the butler. The butler hates
% everyone not richer than Aunt Agatha. The butler hates everyone whom Agatha hates. Noone hates
% everyone. Who killed Agatha?
%
% Save this file as model.mzn. Download `who_killed_agatha.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py who_killed_agatha.json
%   minizinc model.mzn who_killed_agatha_1.json

array[int] of string: names;              % names[1]: Agatha herself, names[2]: the butler, names[3]: Charles
set of int: Residents = index_set(names); % one index per resident, 1-based as in names
int: agatha = 1;                          % index of Agatha in names
int: butler = 2;                          % index of the butler in names
int: charles = 3;                         % index of Charles in names

var Residents: killer;                    % the killer (1-based index into names)
array[Residents, Residents] of var bool: hates;   % hates[i,j]: resident i hates resident j
array[Residents, Residents] of var bool: richer;  % richer[i,j]: resident i is richer than resident j

% richer is asymmetric: nobody is richer than himself or than someone who is richer than him
constraint forall(i, j in Residents)(richer[i,j] -> not richer[j,i]);

% the killer hates the victim, Agatha
constraint hates[killer, agatha];

% the killer is no richer than the victim, Agatha
constraint not richer[killer, agatha];

% Charles hates nobody that Agatha hates
constraint forall(i in Residents)(hates[agatha, i] -> not hates[charles, i]);

% Agatha hates everybody except the butler
constraint forall(i in Residents)(hates[agatha, i] = (i != butler));

% the butler hates everyone not richer than Agatha
constraint forall(i in Residents)(not richer[i, agatha] -> hates[butler, i]);

% the butler hates everyone whom Agatha hates
constraint forall(i in Residents)(hates[agatha, i] -> hates[butler, i]);

% noone hates everyone
constraint forall(i in Residents)(exists(j in Residents)(not hates[i, j]));

solve satisfy;
output ["{\"killer\": ", showJSON(killer - 1), "}"];
