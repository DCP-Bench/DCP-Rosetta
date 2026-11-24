% session2_movie_scheduling: a MiniZinc model from DCP Rosetta.
%
% Consider the following scheduling problem. An actor has been offered to star in n movie projects.
% Each offer comes with the first and last day of filming, and to take the job the actor must be
% available throughout that entire period. The actor cannot accept two jobs whose intervals overlap.
% Each film pays the same fee, so the actor wants the largest possible set of jobs (intervals) such
% that no two of them conflict with each other.
%
% Save this file as model.mzn. Download `session2_movie_scheduling.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session2_movie_scheduling.json
%   minizinc model.mzn session2_movie_scheduling_1.json

% rule 3 splits the mixed-type rows [title, first day, last day] into one array per column
array[int] of string: movies_1;   % movies_1[i]: title of movie i (not used by the model)
array[int] of int: movies_2;      % movies_2[i]: first day of filming of movie i
array[int] of int: movies_3;      % movies_3[i]: last day of filming of movie i

set of int: Movies = index_set(movies_2);            % one index per movie offer

array[Movies] of var bool: selected_movies;          % selected_movies[i]: movie i is accepted

% two movies whose filming periods share a day cannot both be accepted
constraint forall(i, j in Movies where i < j
                  /\ movies_3[i] >= movies_2[j] /\ movies_3[j] >= movies_2[i])(
  not (selected_movies[i] /\ selected_movies[j])
);

var int: objective = sum(i in Movies)(bool2int(selected_movies[i]));

solve maximize objective;
output ["{\"selected_movies\": ", showJSON(selected_movies), "}"];
