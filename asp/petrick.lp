overlapid(X, Y) :- leftimplcvr(X,Z), leftimplcvr(Y,Z), X<Y.

cvrid(Z) :- leftimplcvr(_,Z).

1{ selectimplid(X):leftimplid(X) }.

selectimplcvr(X, Z) :- selectimplid(X), leftimplcvr(X, Z).
selectimpl(X, A, V) :- selectimplid(X), leftimpl(X, A, V).
selectcvrid(Z) :- selectimplcvr(_,Z).

:- cvrid(Z), not selectcvrid(Z).
:- selectimplid(X), selectimplid(Y), X<Y, overlapid(X,Y).
