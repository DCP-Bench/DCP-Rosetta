% session3_exodus: a clingo model from DCP Rosetta.
%
% In preparation for Passover, five children at Hebrew school (Bernice, Carl, Debby, Sammy, and Ted) have been chosen to present different parts of the story of the Exodus from Egypt (burning bush, captivity, Moses's youth, Passover, or the Ten Commandments). Each child is a different age (three, five, seven, eight, or ten), and the family of each child has recently made its own exodus to America from a different country (Ethiopia, Kazakhstan, Lithuania, Morocco, or Yemen). Can you find the age of each child, his or her family's country of origin, and the part of the Exodus story each related?
% 1. Debby's family is from Lithuania.
% 2. The child who told the story of the Passover is two years older than Bernice.
% 3. The child whose family is from Yemen is younger than the child from the Ethiopian family.
% 4. The child from the Moroccan family is three years older than Ted.
% 5. Sammy is three years older than the child who told the story of Moses's youth in the house of the Pharaoh.
% Determine the association: Age-Child-Country-Story.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp
%
% The four categories are given in the order of the problem statement, as 0-based indices: children 0 Bernice,
% 1 Carl, 2 Debby, 3 Sammy, 4 Ted; countries 0 Ethiopia, 1 Kazakhstan, 2 Lithuania, 3 Morocco, 4 Yemen;
% stories 0 burning bush, 1 captivity, 2 Moses's youth, 3 Passover, 4 Ten Commandments; ages 0 three,
% 1 five, 2 seven, 3 eight, 4 ten. Each category is given a number from 1 to 5, and the entities of the
% four categories that share a number belong to the same child.

index(0..4).
value(1..5).

age_years(0,3). age_years(1,5). age_years(2,7). age_years(3,8). age_years(4,10).

% each category assigns the numbers 1 to 5 to its entities, one number each and each number once
1 { ages(I,V) : value(V) } 1 :- index(I).
1 { ages(I,V) : index(I) } 1 :- value(V).
1 { children(I,V) : value(V) } 1 :- index(I).
1 { children(I,V) : index(I) } 1 :- value(V).
1 { countries(I,V) : value(V) } 1 :- index(I).
1 { countries(I,V) : index(I) } 1 :- value(V).
1 { stories(I,V) : value(V) } 1 :- index(I).
1 { stories(I,V) : index(I) } 1 :- value(V).

% the age, family country and story that go with each child, through the shared number
years_of_child(C,Y)   :- children(C,V), ages(A,V), age_years(A,Y).
country_of_child(C,K) :- children(C,V), countries(K,V).
story_of_child(C,S)   :- children(C,V), stories(S,V).

% 1. Debby's family is from Lithuania
:- not country_of_child(2,2).

% 2. the child who told the story of the Passover is two years older than Bernice
:- story_of_child(C,3), years_of_child(C,Y), years_of_child(0,Y0), Y != Y0 + 2.

% 3. the child whose family is from Yemen is younger than the child from the Ethiopian family
:- country_of_child(C1,4), country_of_child(C2,0), years_of_child(C1,Y1), years_of_child(C2,Y2), Y1 >= Y2.

% 4. the child from the Moroccan family is three years older than Ted
:- country_of_child(C,3), years_of_child(C,Y), years_of_child(4,Y4), Y != Y4 + 3.

% 5. Sammy is three years older than the child who told the story of Moses's youth
:- story_of_child(C,2), years_of_child(C,Y), years_of_child(3,Y3), Y3 != Y + 3.

#show ages/2.
#show children/2.
#show countries/2.
#show stories/2.
