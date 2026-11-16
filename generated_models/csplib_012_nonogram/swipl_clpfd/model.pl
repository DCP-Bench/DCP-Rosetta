% csplib_012_nonogram: a SWI-Prolog model from DCP Rosetta.
%
% Nonograms are a popular puzzle, which goes by different names in different countries. Solvers have to shade in squares
% in a grid so that blocks of consecutive shaded squares satisfy constraints given for each row and column. Constraints
% typically indicate the sequence of shaded blocks (e.g. 3,1,2 means that there is a block of 3, then a gap of unspecified
% size, a block of length 1, another gap, and then a block of length 2).
%
% Save this file as model.pl. Download `csplib_012_nonogram.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_012_nonogram.json')" -t halt model.pl
%
% Data fields: rows and cols (the number of rows and of columns), row_rules (the block lengths of each row, top to
% bottom, padded with 0), col_rules (the block lengths of each column, left to right, padded with 0), row_rule_len and
% col_rule_len (the number of block lengths of each rule).
:- use_module(library(clpfd)).

model(Instance, Vars, [board-Board]) :-
    NRows = Instance.rows,
    NCols = Instance.cols,
    RowRules = Instance.row_rules,
    ColRules = Instance.col_rules,
    % Board[R][C] is 1 when the square in row R and column C is shaded, 0 otherwise
    length(Board, NRows),
    maplist(row_of_length(NCols), Board),
    append(Board, Vars),
    Vars ins 0..1,
    % each row shows its block sequence
    maplist(line_shows_blocks, Board, RowRules),
    % each column shows its block sequence
    transpose(Board, Columns),
    maplist(line_shows_blocks, Columns, ColRules).

row_of_length(N, Row) :- length(Row, N).

% the cells of a line (a row or a column) show its blocks, in order: the rule's non-zero entries (zeros are padding)
line_shows_blocks(Cells, Rule) :-
    exclude(==(0), Rule, Blocks),
    blocks_automaton(Blocks, Nodes, Arcs),
    automaton(Cells, Nodes, Arcs).

% The automaton reads the cells from left to right. Its states are gap(I): I blocks are done and the last cell is
% unshaded (or the line has just started), and run(I, J): block I+1 has J shaded cells so far. A block must be followed
% by an unshaded cell before the next block starts, and the line ends in gap(K) (all K blocks done) or with its last
% block complete.
blocks_automaton(Blocks, [source(gap(0)), sink(gap(K))|Sinks], Arcs) :-
    length(Blocks, K),
    findall(Arc, (nth0(I, Blocks, B), block_arc(I, B, Arc)), BlockArcs),
    Arcs = [arc(gap(K), 0, gap(K))|BlockArcs],
    (   K =:= 0
    ->  Sinks = []
    ;   last(Blocks, BK), K1 is K - 1, Sinks = [sink(run(K1, BK))]
    ).

% the transitions for block I+1 of length B: a gap before it, its cells, and the unshaded cell after it
block_arc(I, B, Arc) :-
    (   Arc = arc(gap(I), 0, gap(I))
    ;   Arc = arc(gap(I), 1, run(I, 1))
    ;   between(1, B, J), J < B, J1 is J + 1, Arc = arc(run(I, J), 1, run(I, J1))
    ;   Arc = arc(run(I, B), 0, gap(I1)), I1 is I + 1
    ).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).
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
