% hanging_weights: a SWI-Prolog model from DCP Rosetta.
%
% Thirteen weights, A to M, hang from a system of bars. The weights have different integer values between 1 and 13,
% and must be found so that the diagram balances: the weights on either side of a pivot point are equal when each
% is weighted by its distance from the pivot, and a bar hanging beneath another contributes its total weight as if
% it were a single weight.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% Data fields: none, the problem has no data; the model reads nothing from the instance.
:- use_module(library(clpfd)).

% Distances are counted in units of three characters along the bars, so a weight 9 characters from its pivot
% is 3 units away.
model(_Instance, Vars, [a-A, b-B, c-C, d-D, e-E, f-F, g-G, h-H, i-I, j-J, k-K, l-L, m-M]) :-
    Vars = [A, B, C, D, E, F, G, H, I, J, K, L, M],
    % the weights are different integers from 1 to 13
    Vars ins 1..13,
    all_different(Vars),
    % bottom right bar: C is 5 units left of its pivot and D is 1 unit right, so 5*C = D
    5*C #= D,
    % the bar above it, with G at 3 units left and the bar C+D at 2 units right: 3*G = 2*(C+D)
    3*G #= 2*(C+D),
    % the bar with A and B: A is 4 units left of its pivot and B is 1 unit right, so 4*A = B
    4*A #= B,
    % the bar with E and F: E is 3 units left of its pivot and F is 2 units right, so 3*E = 2*F
    3*E #= 2*F,
    % the bar with H and I, hanging the bar E+F: H is 3 units left, E+F is 2 units right and I is 3 units right
    3*H #= 2*(E+F) + 3*I,
    % the bar with L and M, hanging the bar H+I+E+F: that bar is 1 unit left, L is 1 unit right and M is 4 units right
    H + I + E + F #= L + 4*M,
    % the bar with J and K, hanging the bars A+B and G+C+D: the bar A+B is 3 units left, J is 2 units left,
    % K is 1 unit right and the bar G+C+D is 2 units right
    3*(A + B) + 2*J #= K + 2*(G + C + D),
    % the top bar: the bar H+I+E+F+L+M is 4 units left of the top pivot, and the bar A+B+J+K+G+C+D is 3 units right
    4*(H + I + E + F + L + M) #= 3*(A + B + J + K + G + C + D).

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
