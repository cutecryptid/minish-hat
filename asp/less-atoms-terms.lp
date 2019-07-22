1 { selectsol(S): solution(S) } 1.

selectimpl(X,A,V) :- sol(impl(X,A,V), S), selectsol(S).
selectimplid(X) :- selectimpl(X, _, _).
atomcount(C) :- selectsol(S), C=#count{(X,A) : sol(impl(X,A,V), S), V!=x}.
termcount(C) :- selectsol(S), C=#count{X : sol(impl(X,A,V), S)}.

#preference(p(1), less(weight)){
  X :: atomcount(X)
}.

#preference(p(2), less(weight)){
  X :: termcount(X)
}.

#preference(q, pareto){
  **p(X)
}.

#optimize(q).

#show selectsol/1.
#show selectimpl/3.
#show selectimplid/1.
