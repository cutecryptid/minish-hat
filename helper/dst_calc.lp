atom(0;1;2;z;o;x).
val(0..3).

adj(0,1). adj(0,o).
adj(1,2). adj(2,z).
adj(o,z).

adj(B,A) :- adj(A,B), atom(A), atom(B), A!=B.
nadj(A,B) :- atom(A), atom(B), A!=B, not adj(A,B).

dst(A,A,0) :- atom(A).
dst(A,B,1) :- atom(A), atom(B), adj(A,B).

{ atomval(A,(VX,VY,VZ)) : val(VX), val(VY), val(VZ) } :- atom(A).

:- atom(A), not atomval(A,_).
:- atomval(A, V1), atomval(A,V2), V1 != V2.

valdst(A,B,D,X) :- dst(A,B,D), atomval(A,(VAX,VAY,VAZ)), atomval(B,(VBX,VBY,VBZ)),
                      X=(|VAX-VBX|,|VAY-VBY|,|VAZ-VBZ|).

:- valdst(A,B,D,(VX,VY,VZ)), dst(A,B,D), D!=(VX+VY+VZ).
unadjdst(A,B,D) :- atomval(A,(VAX,VAY,VAZ)), atomval(B,(VBX,VBY,VBZ)), nadj(A,B),
                      D=|VAX-VBX|+|VAY-VBY|+|VAZ-VBZ|.

:- unadjdst(A,B,1).

#show atomval/2.
