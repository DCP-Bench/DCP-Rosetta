% csplib_028_bibd: a MiniZinc model from DCP Rosetta.
%
% Balanced Incomplete Block Design (BIBD) generation is a standard combinatorial problem from design theory, originally
% used in the design of statistical experiments but since finding other applications such as cryptography. It is a
% special case of Block Design, which also includes Latin Square problems.
%
% A BIBD is defined as an arrangement of v distinct objects into b blocks such that each block contains exactly k distinct
% objects, each object occurs in exactly r different blocks, and every two distinct objects occur together in exactly
% lambda blocks. Another way of defining a BIBD is in terms of its incidence matrix, which is a v by b binary matrix with
% exactly r ones per row, k ones per column, and with a scalar product of lambda between any pair of distinct rows.
%
% Save this file as model.mzn. Download `csplib_028_bibd.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_028_bibd.json
%   minizinc model.mzn csplib_028_bibd_1.json

int: v;                                       % the number of objects
int: b;                                       % the number of blocks
int: r;                                       % the number of blocks each object occurs in
int: k;                                       % the number of objects in each block
int: l;                                       % the number of blocks in which every two objects occur together

set of int: Objects = 1..v;                   % the objects, the rows of the incidence matrix
set of int: Blocks = 1..b;                    % the blocks, the columns of the incidence matrix

% matrix[i,j]: object i is in block j
array[Objects, Blocks] of var bool: matrix;

% each object occurs in exactly r blocks
constraint forall(i in Objects)(sum(j in Blocks)(bool2int(matrix[i, j])) = r);

% each block contains exactly k objects
constraint forall(j in Blocks)(sum(i in Objects)(bool2int(matrix[i, j])) = k);

% every two distinct objects occur together in exactly l blocks
constraint forall(i in Objects, i2 in Objects where i < i2)(
    sum(j in Blocks)(bool2int(matrix[i, j] /\ matrix[i2, j])) = l);

solve satisfy;

output ["{\"matrix\": ", showJSON(matrix), "}"];
