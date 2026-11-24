% allergy: a clingo model from DCP Rosetta.
%
% Four friends (two women named Debra and Janet, and two men named Hugh and Rick) found that each of them is allergic to something different: eggs, mold, nuts and ragweed. We would like to match each one's surname (Baxter, Lemon, Malone and Fleet) with his or her allergy. We know that: Rick is not allergic to mold; Baxter is allergic to eggs; Hugh is neither surnamed Lemon nor Fleet; Debra is allergic to ragweed; Janet (who isn't Lemon) is neither allergic to eggs nor to mold.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% The friends are numbered Debra 0, Janet 1, Hugh 2, Rick 3.
friend(0..3).
food(eggs;mold;nuts;ragweed).
name(baxter;lemon;malone;fleet).

% each friend has exactly one allergy, and each allergy belongs to exactly one friend
1 { allergy(F,X) : food(X) } 1 :- friend(F).
1 { allergy(F,X) : friend(F) } 1 :- food(X).

% each friend has exactly one surname, and each surname belongs to exactly one friend
1 { surname(F,N) : name(N) } 1 :- friend(F).
1 { surname(F,N) : friend(F) } 1 :- name(N).

% Rick is not allergic to mold
:- allergy(3,mold).

% Baxter is allergic to eggs
:- surname(F,baxter), not allergy(F,eggs).

% Hugh is neither surnamed Lemon nor Fleet
:- surname(2,lemon).
:- surname(2,fleet).

% Debra is allergic to ragweed
:- not allergy(0,ragweed).

% Janet is not surnamed Lemon, and is neither allergic to eggs nor to mold
:- surname(1,lemon).
:- allergy(1,eggs).
:- allergy(1,mold).

% the friend with each allergy and each surname
eggs(F) :- allergy(F,eggs).
mold(F) :- allergy(F,mold).
nuts(F) :- allergy(F,nuts).
ragweed(F) :- allergy(F,ragweed).
baxter(F) :- surname(F,baxter).
lemon(F) :- surname(F,lemon).
malone(F) :- surname(F,malone).
fleet(F) :- surname(F,fleet).

#show eggs/1.
#show mold/1.
#show nuts/1.
#show ragweed/1.
#show baxter/1.
#show lemon/1.
#show malone/1.
#show fleet/1.
