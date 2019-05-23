#include <incmode>.

%% t = 0
#program base.
holds(m(X,A,V), 0):- m(X, A, V).
symbol(0;1;2;z;o;x).
pair(0, 1, z). pair(1, 0, z).
pair(1, 2, o). pair(2, 1, o).
pair(z, o, x). pair(o, z, x).

value(V, V) :- symbol(V), V <= 2.
value(z, 3). value(o, 4). value(x, 5).

%% t > 0
#program step(t).
holds(m((X,Y),A,P), t) :- vadj(X,Y,A,P,t-1), holds(m(X,A,V),t-1), holds(m(Y,A,W),t-1).
holds(m((X,Y),A,V), t) :- vadj(X,Y,_,_,t-1), holds(m(X,A,V),t-1), holds(m(Y,A,V),t-1).

%% t >= 0
#program check(t).
id(X,t) :- holds(m(X,A,V),t).
sumvalue(X, S, t) :- id(X, t), S=#sum{ W,A,V : holds(m(X,A,V),t), value(V,W) }.

adj(X,Y,t) :- id(X,t), id(Y,t), X<Y, sumvalue(X,SX,t), sumvalue(Y,SY,t), |SX-SY|=1,
              #count{A: holds(m(X,A,V),t), holds(m(Y,A,W),t), V!=W}=1.

vadj(X,Y,A,P,t) :- adj(X,Y,t), holds(m(X,A,V),t), holds(m(Y,A,W),t), pair(V,W,P).

:- query(T), T < steps.

#show adj/3.
#show sumvalue/3.
#show holds/2.
#show id/2.
