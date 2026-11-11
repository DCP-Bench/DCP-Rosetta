% csplib_012_nonogram: a MiniZinc model from DCP Rosetta.
%
% Nonograms are a puzzle in which the solver shades squares in a grid so that the blocks of
% consecutive shaded squares satisfy the constraints given for each row and each column.
% A constraint is the sequence of shaded blocks: 3,1,2 means a block of 3, then a gap of
% unspecified size, a block of length 1, another gap, and a block of length 2.
%
% Save this file as model.mzn. Download `csplib_012_nonogram.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_012_nonogram.json
%   minizinc model.mzn csplib_012_nonogram_1.json

int: rows;                                          % the number of rows
int: cols;                                          % the number of columns
int: row_rule_len;                                  % the width of the padded row rules
int: col_rule_len;                                  % the width of the padded column rules
set of int: Rows = 1..rows;                         % one index per row
set of int: Cols = 1..cols;                         % one index per column
set of int: RowSlots = 1..row_rule_len;             % one slot per entry of a row rule
set of int: ColSlots = 1..col_rule_len;             % one slot per entry of a column rule

% row_rules[r, k]: the k-th block length of row r, 0 for unused slots
array[Rows, RowSlots] of int: row_rules;
% col_rules[c, k]: the k-th block length of column c, 0 for unused slots
array[Cols, ColSlots] of int: col_rules;

% board[r, c] = 1 if the square is shaded, 0 otherwise
array[Rows, Cols] of var 0..1: board;

% A line of squares has the shaded blocks given by its rule (zero entries are unused slots).
% start[k] is the first square of block k: each block fits in the line, blocks are in order,
% and consecutive blocks have at least one unshaded square between them.
predicate line_has_blocks(array[int] of var int: line, array[int] of int: rule) =
    let {
        % the block lengths of the rule, in order, without the unused slots
        array[int] of int: blocks = [rule[k] | k in index_set(rule) where rule[k] > 0];
        int: nb = length(blocks);
        int: n = length(line);
        % the first square of each block
        array[1..nb] of var 1..n: start;
    } in
    forall(k in 1..nb)(start[k] + blocks[k] - 1 <= n) /\
    forall(k in 1..nb - 1)(start[k + 1] >= start[k] + blocks[k] + 1) /\
    forall(i in index_set(line))(line[i] = 1 <-> exists(k in 1..nb)(start[k] <= i /\ i < start[k] + blocks[k]));

% the shaded blocks of each row match its rule
constraint forall(r in Rows)(line_has_blocks([board[r, c] | c in Cols], [row_rules[r, k] | k in RowSlots]));

% the shaded blocks of each column match its rule
constraint forall(c in Cols)(line_has_blocks([board[r, c] | r in Rows], [col_rules[c, k] | k in ColSlots]));

solve satisfy;
output ["{\"board\": ", showJSON(board), "}"];
