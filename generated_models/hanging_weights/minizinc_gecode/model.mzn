% hanging_weights: a MiniZinc model from DCP Rosetta.
%
% The diagram shows weights A to M (thirteen of them) hanging from a system of bars. The weights are
% different integers between 1 and 13, and the task is to find the weights that make every bar balance
% as drawn. Each three characters along a bar are one unit of distance. The rules: (1) the weights on
% either side of a pivot point are equal when weighted by their distance from the pivot, and (2) a bar
% hanging beneath another contributes its total weight as though it were a single weight.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: N = 13;                                     % the largest weight value, and the number of weights

% the weights A to M, each an integer from 1 to N
var 1..N: a; var 1..N: b; var 1..N: c; var 1..N: d; var 1..N: e; var 1..N: f; var 1..N: g;
var 1..N: h; var 1..N: i; var 1..N: j; var 1..N: k; var 1..N: l; var 1..N: m;

% the weights have different values
constraint all_different([a, b, c, d, e, f, g, h, i, j, k, l, m]);

% the bar with A and B balances: 4*A = B
constraint 4 * a = b;
% the bottom right bar with C and D balances: 5*C = D
constraint 5 * c = d;
% the bar with E and F balances: 3*E = 2*F
constraint 3 * e = 2 * f;
% the bar with G, which carries C and D as one weight, balances: 3*G = 2*(C+D)
constraint 3 * g = 2 * (c + d);
% the bar with J and K, which carries A+B and G+C+D as single weights, balances: 3*(A+B) + 2*J = K + 2*(G+C+D)
constraint 3 * (a + b) + 2 * j = k + 2 * (g + c + d);
% the bar with H and I, which carries E+F as one weight, balances: 3*H = 2*(E+F) + 3*I
constraint 3 * h = 2 * (e + f) + 3 * i;
% the bar with L and M, which carries H+I+E+F as one weight, balances: H+I+E+F = L + 4*M
constraint h + i + e + f = l + 4 * m;
% the top bar balances its two hanging groups: 4*(L+M+H+I+E+F) = 3*(J+K+G+A+B+C+D)
constraint 4 * (l + m + h + i + e + f) = 3 * (j + k + g + a + b + c + d);

solve satisfy;

output ["{\"a\": ", showJSON(a), ", \"b\": ", showJSON(b), ", \"c\": ", showJSON(c), ", \"d\": ", showJSON(d),
        ", \"e\": ", showJSON(e), ", \"f\": ", showJSON(f), ", \"g\": ", showJSON(g), ", \"h\": ", showJSON(h),
        ", \"i\": ", showJSON(i), ", \"j\": ", showJSON(j), ", \"k\": ", showJSON(k), ", \"l\": ", showJSON(l),
        ", \"m\": ", showJSON(m), "}"];
