import argparse
import clingo
import re
import sys
import subprocess
import time

def input_to_asp(input_file):
    asp_facts = ""
    with open(input_file) as input_text:
        for line in input_text:
            if re.match('^[012ozx]+\s*$', line):
                m = line.strip()
                mr = m.replace('o','3').replace('z','4').replace('x','5')
                i = int(mr, 6)
                for idx,bit in enumerate(m):
                    asp_facts += "m({0}, {1}, {2}). ".format(i, "x"+str(idx), bit)
                asp_facts += "\n"
    return asp_facts

def symbols_to_facts(symbols):
    return " ".join(["{0}.".format(sym) for sym in symbols])

def symbols_to_dict(symbols, steps):
    steps = { }
    for sym in symbols:
        if not sym.arguments[-1].number in steps:
            steps.update({ sym.arguments[-1].number : { 'impl': { }, 'adj': [], 'sum': { }  } })
        if sym.name == 'holds':
            m,s = sym.arguments
            x,a,v = m.arguments
            s,x,a,v = s.number, str(x), str(a), str(v)
            if not x in steps[s]['impl'].keys():
                steps[s]['impl'].update({ x : [(a,v)] })
            else:
                steps[s]['impl'][x] += [(a,v)]
        elif sym.name == 'adj':
            x,y,s = sym.arguments
            x,y,s = str(x), str(y), s.number
            steps[s]['adj'] += [ (x,y) ]
        elif sym.name == 'sumvalue':
            x,c,s = sym.arguments
            x,c,s = str(x), c.number, s.number
            if not c in steps[s]['sum'].keys():
                steps[s]['sum'].update({ c : [x] })
            else:
                steps[s]['sum'][c] += [x]
    return steps

def pretty_dict(stepdict):
    ret = ""
    for sk in sorted(stepdict.keys()):
        ret += "STEP {0}\n".format(sk)
        step = stepdict[sk]
        for sumk in sorted(step['sum'].keys()):
            ret += "  WEIGHT {0}:\n".format(sumk)
            for ak in step['sum'][sumk]:
                label = ""
                for atom in sorted(step['impl'][ak]):
                    label += atom[1]
                ret += "    {0}  {1} \n".format(ak, label)
        if len(step['adj']) > 0:
            ret += "  ADJACENT\n"
            for adj in sorted(step['adj']):
                ret += "    [{0},{1}]".format(adj[0], adj[1])
                adj_id = "({0},{1})".format(adj[0], adj[1])
                if sk+1 in stepdict.keys():
                    new = sorted(stepdict[sk+1]['impl'][adj_id])
                    nlabel = ""
                    for a,v in new:
                        nlabel += v
                    ret += " {0}".format(nlabel)
                ret += "\n"
    return ret



def solve_iter(asp_program, asp_facts, steps):
    prg = clingo.Control([])
    prg.add("check", ["k"], "#external query(k).")
    prg.add("check", [], "#const steps={0}.".format(steps))
    prg.load("./"+asp_program+".lp")
    for f in asp_facts:
        prg.add("base", [], f)

    step, handle, ret = 0, None, []
    while ( step == 0 or not handle.get().satisfiable ):
        parts = []
        parts.append(("check", [step]))
        if step > 0:
            prg.release_external(clingo.Function("query", [step-1]))
            parts.append(("step", [step]))
            prg.cleanup()
        else:
            parts.append(("base", []))
        prg.ground(parts)
        prg.assign_external(clingo.Function("query", [step]), True)
        step += 1
        handle = prg.solve(yield_=True)
        for m in handle:
            ret = m.symbols(shown=True)
    return ret


def main():
    parser = argparse.ArgumentParser(description='Minterm reduction with ASP')
    parser.add_argument('input_sample', metavar='I', type=str,
                        help='route for the minterm text file')
    parser.add_argument('steps', metavar='S', type=int,
                        help='number of steps of solving')
    args = parser.parse_args()

    # Turn minterms into ASP facts
    start_time = time.time()
    input_facts = input_to_asp(args.input_sample)
    input_conversion_time = time.time()
    print("Input to ASP: {0:.5f} s".format(input_conversion_time-start_time))

    # Create the prime implicates
    pre_pair_time = time.time()
    primpl_syms = solve_iter("stepped-pair-maker", [input_facts], args.steps)
    post_pair_time = time.time()
    print("Pairmaking: {0:.5f} s".format(post_pair_time-pre_pair_time))

    resdict = symbols_to_dict(primpl_syms, args.steps)
    print(pretty_dict(resdict))

    finished = False
    for s in sorted(resdict.keys()):
        if len(resdict[s]['adj']) == 0:
            print("No more adjacent minterms! Finished in {0} steps!".format(s))
            finished = True
    if not finished:
        print("Keep going, there are still adjacent minterms...")

    end_time = time.time()
    print("Total: {0:.5f} s".format(end_time-start_time))

if __name__ == "__main__":
    sys.settrace
    main()
