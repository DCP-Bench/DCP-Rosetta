% csplib_006_golomb_rulers: a SWI-Prolog model from DCP Rosetta.
%
% A Golomb ruler is a set of m integers 0 = a_1 < a_2 < ... < a_m such that the m(m-1)/2 differences a_j - a_i
% (1 <= i < j <= m) are all distinct. Such a ruler has m marks and its length is a_m. Find a ruler with the minimum
% length for the given number of marks: these rulers have applications such as sensor placements in x-ray
% crystallography and radio astronomy.
%
% Save this file as model.pl. Download `csplib_006_golomb_rulers.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_006_golomb_rulers.json')" -t halt model.pl
%
% Data fields: size (the number of marks m).
:- use_module(library(clpfd)).

model(Instance, Marks, [marks-Marks, length-Length], min(Length)) :-
    Size = Instance.size,
    % an upper bound on the position of a mark (the optimal ruler is shorter than size * size)
    % an upper bound on the position of a mark (the optimal ruler is shorter than size * size)
    Longest is Size * Size,
    % Marks[I] is the position of mark I+1
    length(Marks, Size),
    Marks ins 0..Longest,
    % the first mark is at 0, and the marks are strictly increasing
    Marks = [First|_],
    First #= 0,
    chain(Marks, #<),
    % the length of the ruler is the position of the last mark
    last(Marks, Length),
    % the differences between any two marks are all distinct
    findall(I-J, (between(1, Size, I), between(1, Size, J), I < J), Pairs),
    maplist(difference(Marks), Pairs, Differences),
    all_distinct(Differences).

% the difference between marks J and I (I < J)
difference(Marks, I-J, Difference) :-
    nth1(I, Marks, Earlier),
    nth1(J, Marks, Later),
    Difference #= Later - Earlier.

:- use_module(library(http/json)).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
