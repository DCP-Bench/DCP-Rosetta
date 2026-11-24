% session2_movie_scheduling: a clingo model from DCP Rosetta.
%
% Imagine you are a highly-in-demand actor, who has been presented with offers to star in n different movie projects under development. Each offer comes specified with the first and last day of filming. To take the job, you must commit to being available throughout this entire period. Thus, you cannot simultaneously accept two jobs whose intervals overlap. Each of these films pays the same fee per film, so you seek the largest possible set of jobs (intervals) such that no two of them conflict with each other.
%
% Save this file as model.lp. Download `session2_movie_scheduling.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session2_movie_scheduling.json
%   python -m clingo model.lp session2_movie_scheduling_1.lp
%
% Input: movies(I, 0, Title), movies(I, 1, FirstDay), movies(I, 2, LastDay) hold the title, first filming
% day and last filming day of movie I (indices are 0-based, as in the data).

movie(I) :- movies(I, 0, _).

% each movie is either accepted (selected(I)) or not
{ selected(I) } :- movie(I).

% two different movies overlap when each one ends on or after the day the other starts
overlap(I, J) :- movie(I), movie(J), I < J,
    movies(I, 1, StartI), movies(I, 2, EndI),
    movies(J, 1, StartJ), movies(J, 2, EndJ),
    EndI >= StartJ, EndJ >= StartI.

% two jobs whose filming periods overlap cannot both be accepted
:- selected(I), selected(J), overlap(I, J).

% the number of accepted movies is as large as possible
#maximize { 1, I : selected(I) }.

% the output: true for each movie accepted, false otherwise, in the order of the input list
selected_movies(I, true)  :- selected(I).
selected_movies(I, false) :- movie(I), not selected(I).

#show selected_movies/2.
