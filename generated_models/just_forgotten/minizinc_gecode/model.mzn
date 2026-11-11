% just_forgotten: a MiniZinc model from DCP Rosetta.
%
% Joe forgot one of his bank account numbers. He remembered that it has all the digits from 0 to n-1 in
% some order, and he tried a number of sets without success. In each set, just a specific number of the
% digits were in their correct position. Given that number for each set, work out the account number.
%
% Save this file as model.mzn. Download `just_forgotten.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py just_forgotten.json
%   minizinc model.mzn just_forgotten_1.json

include "globals.mzn";

array[int, int] of int: sets;                    % sets[g,i]: the digit at position i of guess g
int: num_correct_digits;                         % the number of digits in correct position in every guess

set of int: Guesses = index_set_1of2(sets);      % the guesses
set of int: Positions = index_set_2of2(sets);    % the digit positions
int: n = card(Positions);                        % the number of digits
set of int: Digits = 0..n - 1;                   % the digits of the account number

% x[i]: the digit at position i of the account number
array[Positions] of var Digits: x;

% the account number uses every digit exactly once
constraint all_different(x);

% each guess has exactly num_correct_digits digits in their correct positions
constraint forall(g in Guesses)(
    sum(i in Positions)(bool2int(x[i] = sets[g, i])) = num_correct_digits);

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
