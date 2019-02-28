
covers(X, X, 0) :- m(X, A, V).
pair(0, 1, n). pair(1, 0, n).
pair(1, 2, p). pair(2, 1, p).
pair(n, p, x). pair(p, n, x).

m((X,Y),A,P) :- vadj(X,Y,A,P), m(X,A,V), m(Y,A,W).
m((X,Y),A,V) :- vadj(X,Y,_,_), m(X,A,V), m(Y,A,V).

id(X) :- m(X,A,V).
adj(X,Y) :- id(X), id(Y), X<Y, #count{A: m(X,A,V), m(Y,A,W), V!=W }=1.
vadj(X,Y,A,P) :- adj(X,Y), m(X,A,V), m(Y,A,W), pair(V,W,P).

mark(Y) :- vadj(X,Y,A,P), P != x.
unmark(X) :- id(X), not mark(X).

#show mark/1.
#show unmark/1.
#show vadj/4.
