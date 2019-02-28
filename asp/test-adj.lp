pair(0, 1, n). pair(1, 0, n).
pair(1, 2, p). pair(2, 1, p).
pair(n, p, x). pair(p, n, x).

id(X) :- m(X,A,V).

adj(X,Y) :- id(X), id(Y), X<Y, #count{A: m(X,A,V), m(Y,A,W), V!=W }=1.
vadj(X,Y,P) :- adj(X,Y), m(X,A,V), m(Y,A,W), pair(V,W,P).

#show vadj/3.
