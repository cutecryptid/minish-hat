import argparse
import clingo
import re
import sys
import time
import copy
from itertools import product

def totalize(s):
    keyletters = '21'
    seq = list(s)
    indices = [ i for i, c in enumerate(seq) if c in keyletters ]
    ret = []
    for t in product(keyletters, repeat=len(indices)):
        for i, c in zip(indices, t):
            seq[i] = c
        ret += [''.join(seq)]
    return ret

def get_label_weight(label):
    weight = { '0' : 0, '1': 0, '2': 0,
                'z' : 1, 'o': 1, '-': 2, 'x': 2 }
    sum = 0
    for i in label:
        sum += weight[i]
    return sum

def parse_input(file_contents):
    dict = {}
    for line in file_contents.split('\n'):
        if re.match('^[012ozx]+\s*$', line):
            m = line.strip()
            i = get_id(m)
            dict.update({ frozenset([i]) : { 'label' : m, 'mark': False,
                         'weight' : get_label_weight(m),
                         'adjval' : get_adjval(m) } })
    return dict

def get_adjval(label):
    labelr = label.replace('o','4').replace('z','3').replace('x','5')
    return sum([ int(x) for x in labelr ])

def get_id(label):
    labelr = label.replace('o','4').replace('z','3').replace('x','5')
    return int(labelr, 6)

def get_similar_marks(position, label, reverse_dict):
    ret = []
    reg = r"" + label[:position] + r"[012oz]" + label[position+1:]
    for tlab in reverse_dict.keys():
        if re.search(reg, tlab, re.IGNORECASE):
            ret += [reverse_dict[tlab]]
    return ret

def check_adjacent(labelx, labely):
    pairs = {
        ('1', '2') : ('o', 0),
        ('2', '1') : ('o', 1),
        ('0', '1') : ('z', 1),
        ('1', '0') : ('z', 0),
        ('o', 'z') : ('x', 0),
        ('z', 'o') : ('x', 0)
    }
    adjcount = 0
    for i in range(len(labelx)):
        if (labelx[i], labely[i]) in pairs.keys():
            r,p = pairs[(labelx[i], labely[i])]
            ret = (i, r, p)
            adjcount += 1
            if adjcount > 1:
                ret = (-1, None, -1)
                break
        elif labelx[i] != labely[i]:
            ret = (-1, None, -1)
            break
    return ret

def mincover_facts(label_cover_dict):
    facts = ""
    for k,v in label_cover_dict.items():
        facts += "leftid(\"{0}\"). ".format(k)
        for val in v:
            facts += "covers(\"{0}\", {1}). ".format(k, val)
        facts += "\n"
    return facts

def solve(asp_program, asp_facts, clingo_args):
    c = clingo.Control(clingo_args)
    if asp_program != "":
        c.load("./asp/"+asp_program+".lp")
    for facts in asp_facts:
        c.add("base", [], facts)
    c.ground([("base", [])])
    ret = []
    with c.solve(yield_=True) as handle:
        for m in handle:
            ret += [m.symbols(shown=True)]
    return ret

def labels_to_rules(labels):
    terms = []
    for label in labels:
        head, body = [], []
        for idx,v in enumerate(label):
            if v == "0":
                body += [ "not x" + str(idx) ]
            elif v == "2":
                body += [ "x" + str(idx) ]
            elif v == "o":
                head += [ "not x" + str(idx) ]
            elif v == "z":
                head += [ "x" + str(idx) ]
            elif v == "1":
                head += [ "x{0} v not x{0}".format(str(idx)) ]
        term = [ ]
        if len(head) > 0:
            term += [ " v ".join(head) ]
        if len(body) > 0:
            term += [ " ^ ".join(body) ]
        terms += [ " :- ".join(term) + "." ]
    return "\n".join(terms)


def main():
    parser = argparse.ArgumentParser(description='Minterm reduction with ASP')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin, help="TXT File (default: stdin)")
    parser.add_argument('-t', '--time', type=int, default=-1,
                    help="show different stages' times, 0 means everything")
    parser.add_argument('-v', '--verbose', type=int, default=-1,
                    help="show some more text than usual, 0 means everything")
    parser.add_argument('-m', '--maxstep', type=int,
                    help="fix maximum number of steps")
    parser.add_argument('-o','--optmode', default="atoms",
                    choices=['atoms', 'terms'],
                    help='formulae minimization method')
    parser.add_argument('-a', '--all', action='store_true', default=False,
                    help='enumerate all optimal models')
    args = parser.parse_args()

    if args.verbose == None:
        args.verbose = -1

    if args.time == None:
        args.time = -1

    start_time = time.time()
    try:
        input_dict = parse_input(args.file.read())
    except Exception as exc:
        print("error parsing file:", args.file.name)
        print(exc)
        return 1


    init_minterms = dict()
    for k,v in input_dict.items():
        label = v['label']
        is_total = False
        total_cover_ids = []
        if re.match(r"^[0,2]+$", label):
            is_total = True
            total_cover = totalize(label)
            total_cover_ids = [ int(lb, 6) for lb in total_cover]
        init_minterms.update( { k : { 'label' : v['label'],  'is_total' : is_total,
                                'total_cover':  frozenset(sorted(total_cover_ids)) }})

    parse_time = time.time()

    if args.time == 0 or args.time >= 2:
        print("Initial Dictionary (w/ total cover) build: {0:.5f} s".format(parse_time-start_time))

    rev_dict = {v['label']: k for k, v in input_dict.items()}

    rev_build_time = time.time()

    if args.time == 0 or args.time >= 2:
        print("Reverse Dictionary build: {0:.5f} s".format(rev_build_time-parse_time))

    if args.maxstep != None:
        maxstep = args.maxstep-1
    else:
        maxstep = len(list(rev_dict.keys())[0])*2

    adj_left = True
    step = 0
    pre_pair_time = time.time()
    iteration_time = time.time()
    while adj_left and step <= maxstep:
        pre_filter_terms = time.time()
        selected_minterms = { k: v for k, v in input_dict.items()
                                if (v['weight'] == step and not v['mark']) }
        if args.verbose == 0 or args.verbose >= 2:
            print("\t{0} elements of weight {1}".format(len(selected_minterms),step))
        post_filter_terms = time.time()
        if args.time == 0 or args.time >= 3:
            print("\tSTEP {0} Minterms filter by weight: {1:.5f} s".format(step, post_filter_terms-pre_filter_terms))
        adj_vals = dict()
        for key, value in selected_minterms.items():
            adj_vals.setdefault(value['adjval'], list()).append(key)
        post_population_adjvals = time.time()
        if args.time == 0 or args.time >= 3:
            print("\tSTEP {0} AdjVals Population: {1:.5f} s".format(step, post_population_adjvals-post_filter_terms))

        adj_vals_keys = sorted(adj_vals.keys())
        for i in range(len(adj_vals_keys)-1):
            pre_pair_loop = time.time()
            lw, hw = adj_vals_keys[i:i+2]
            if args.verbose == 0 or args.verbose >= 3:
                print("\tPerforming {0} parity checks for weights [{1},{2}]"
                    .format(len(adj_vals[lw])*len(adj_vals[hw]),lw, hw))
            for idx in adj_vals[lw]:
                for idy in adj_vals[hw]:
                    lx = selected_minterms[idx]['label']
                    ly = selected_minterms[idy]['label']
                    v = check_adjacent(lx, ly)
                    if v[0] >= 0:
                        nlx = lx[:v[0]] + v[1] + lx[v[0]+1:]
                        nid = frozenset(sorted(list(idx)+list(idy)))
                        input_dict.update({ nid : { 'label' : nlx,
                                     'mark': False,
                                     'weight' : get_label_weight(nlx),
                                     'adjval' : get_adjval(nlx) } })
                        rev_dict.update({ nlx: nid })
                        if v[1] == 'x':
                            marked_ids = get_similar_marks(v[0], nlx, rev_dict)
                            for mark in marked_ids:
                                input_dict[mark]['mark'] = True
                        else:
                            marked_id = [idx,idy][v[2]]
                            input_dict[marked_id]['mark'] = True
            post_pair_loop = time.time()
            if args.time == 0 or args.time >= 4:
                print("\tSTEP {0}, [{1},{2}] Pair Time: {3:.5f} s".format(step, lw, hw,
                    post_pair_loop-pre_pair_loop))
        if len(adj_vals_keys) == 0:
            adj_left = False
        post_iteration_time = time.time()
        if args.time == 0 or args.time >= 3:
            print("STEP {0}, Subtotal Pair Time: {1:.5f} s".format(step,
                post_iteration_time-iteration_time))
        iteration_time = time.time()
        step += 1
    if args.time == 0 or args.time >= 2:
        print("Total Pair Time: {0:.5f} s".format(iteration_time-pre_pair_time))

    pre_prime = time.time()
    unmarked = { k: v for k, v in input_dict.items() if not v['mark'] }
    post_prime = time.time()
    if args.time == 0 or args.time >= 2:
        print("Prime Implicates Dictionary build: {0:.5f} s".format(post_prime-pre_prime))

    pre_extend = time.time()
    extended_cover_unmarked = dict()
    for k, v in unmarked.items():
        ext_cover = k
        for e in list(k):
            if init_minterms[frozenset([e])]['is_total']:
                ext_cover |= init_minterms[frozenset([e])]['total_cover']
        extended_cover_unmarked.update( { k : dict(v, **{ 'covers': ext_cover,
                                'is_essential' : False } ) } )
    post_extend = time.time()
    if args.time == 0 or args.time >= 2:
        print("Prime Implicates Total Coverage Calculation: {0:.5f} s".format(post_extend-pre_extend))

    if args.verbose == 0 or args.verbose >= 1:
        print("PRIME IMPLICATES WITH TOTAL COVERAGE")
        for k,v in extended_cover_unmarked.items():
            covers = list(v['covers'])
            label_covers = [init_minterms[frozenset([x])]['label'] for x in covers]
            print("[{0}] : ({1})".format(v['label'], " ".join(label_covers)))

    pre_covered_by = time.time()
    cover_dict = dict()
    for ik, iv in init_minterms.items():
        for uk, uv in extended_cover_unmarked.items():
            if len(ik & uv['covers']) == 1:
                if not ik in cover_dict.keys():
                    cover_dict.update( { ik: { 'covered_by' : [ { uk : uv['label'] } ],
                                'label' : iv['label'], 'is_used' : False } } )
                else:
                    cover_dict[ik]['covered_by'] += [ { uk : uv['label'] } ]
    post_covered_by = time.time()
    if args.time == 0 or args.time >= 2:
        print("Minterms Covered Dictionary Build: {0:.5f} s".format(post_covered_by-pre_covered_by))

    if args.verbose == 0 or args.verbose >= 2:
        print("MINTERMS COVERED BY IMPLICATES")
        for k,v in sorted(cover_dict.items()):
            cover = []
            for x in v['covered_by']:
                for cv in x.values():
                    cover += [cv]
            print("[{0}] : ({1})".format(v['label'], ", ".join(cover)))

    essential_implicates = dict()
    step = 0
    fullcover = False
    pre_essential = time.time()
    if args.verbose == 0 or args.verbose >= 1:
        print("ESSENTIAL IMPLICATES EXTRACTION")
    while True:
        essential_iter = time.time()
        if args.verbose == 0 or args.verbose >= 2:
            print("\tSTEP {0}".format(step))
        essential_count = 0
        unused_cover_dict = { k : v for k, v in cover_dict.items() if not v['is_used']}
        if args.verbose == 0 or args.verbose >= 2:
            print("\tUnused minterms {0}".format(len(unused_cover_dict.items())))
        if len(unused_cover_dict.items()) == 0:
            fullcover = True
            break
        for ck, cv in unused_cover_dict.items():
            if len(cv['covered_by']) == 1:
                essential_count += 1
                for ek, ev in cv['covered_by'][0].items():
                    essential_cover = extended_cover_unmarked[ek]['covers']
                    essential_implicates.update({ ek : { 'label' : ev, 'covers':essential_cover } })
                    extended_cover_unmarked[ek]['is_essential'] = True
                    for minid in list(essential_cover):
                        cover_dict[frozenset([minid])]['is_used'] = True
        if essential_count == 0:
            break
        if args.verbose == 0 or args.verbose >= 2:
            print("\tFound {0} minterms covered by a single implicate".format(essential_count))
            for k,v in essential_implicates.items():
                print("\t[{0}] : ({1})".format(v['label'], list(k)))
        post_essential_iter = time.time()
        if args.time == 0 or args.time >= 3:
            print("STEP {0} Implicate Extraction: {1:.5f} s".format(step,
                    post_essential_iter-essential_iter))
        step += 1
        essential_iter = time.time()
    post_essential = time.time()
    if args.time == 0 or args.time >= 2:
        print("Essential Implicates Extraction: {0:.5f} s".format(post_essential-pre_essential))

    if args.verbose == 0 or args.verbose >= 1:
        for k,v in essential_implicates.items():
            print("[{0}] : ({1})".format(v['label'], list(k)))

    essential_labels = [v['label'] for k,v in essential_implicates.items()]

    if fullcover:
        if args.verbose == 0 or args.verbose >= 1:
            print("Achieved full coverage, no need for Petrick")
        final_labels = [essential_labels]
    else:
        prime_left = { k : v for k, v in extended_cover_unmarked.items() if not v['is_essential']}
        if args.verbose == 0 or args.verbose >= 1:
            print("UNCOVERED MINTERMS: {0}".format(len(unused_cover_dict.items())))
            if args.verbose >= 2:
                for uk, uv in unused_cover_dict.items():
                    print("[{0}] : ({1})".format(uv['label'], list(uk)))
            print("NON-ESSENTIAL PRIME IMPLICATES: {0}".format(len(prime_left.items())))
            if args.verbose >= 2:
                for uk, uv in prime_left.items():
                    print("[{0}] : ({1})".format(uv['label'], list(uv['covers'])))

        pre_petrick_facts = time.time()
        minids = set()
        for k in unused_cover_dict.keys():
            minids.add(list(k)[0])
        label_cover = {}
        for k,v in prime_left.items():
            limited_cover = set(v['covers']) & minids
            if len(limited_cover) > 0:
                label_cover.update( { v['label'] : limited_cover } )

        petrick_facts = mincover_facts(label_cover)
        post_petrick_facts = time.time()
        if args.time == 0 or args.time >= 2:
            print("Petrick Facts Generation: {0:.5f} s".format(post_petrick_facts-pre_petrick_facts))
        petrick_solutions = solve('petrick_hybrid', [petrick_facts], ["0"])
        post_petrick_solve = time.time()
        if args.time == 0 or args.time >= 2:
            print("Petrick Solving: {0:.5f} s".format(post_petrick_solve-post_petrick_facts))

        final_labels = []
        for sol in petrick_solutions:
            for sym in sol:
                selected_labels = []
                if sym.name == "selectid":
                    label = str(sym.arguments[0])[1:-1]
                    selected_labels += [label]
            final_labels += [essential_labels + selected_labels]

    pre_min_time = time.time()
    if args.time == 0 or args.time >= 1:
        print("Pre-Minimization Time: {0:.5f} s".format(pre_min_time-start_time))

    if args.verbose == 0 or args.verbose >= 1:
        for idx,sol in enumerate(final_labels):
            print("SOLUTION #{0}".format(idx))
            print(labels_to_rules(sol))

    if len(final_labels) > 1:
        minimize_facts = ""
        for solnum,sol in enumerate(final_labels):
            minimize_facts += "solution({0}).\n".format(solnum)
            for label in sol:
                id_list = [str(x) for x in sorted(list(rev_dict[label]))]
                label_id = "({0})".format(", ".join(id_list))
                for i,v in enumerate(label):
                    minimize_facts += "sol(impl({0},x{1},{2}), {3}). ".format(
                                label_id, i, v, solnum)
                minimize_facts += "\n"

        if args.all:
            minimal_solutions = solve("less-"+args.optmode, [minimize_facts], ["--opt-mode=optN","-n0"])
            # The first solution appears two times, so drop it
            minimal_solutions = minimal_solutions[1:]
        else:
            minimal_solutions = solve("less-"+args.optmode, [minimize_facts], [])

        sorted_solutions = []
        for msol in minimal_solutions:
            for sym in msol:
                if sym.name == "selectsol":
                    solnum = sym.arguments[0].number
                    sorted_solutions += [final_labels[solnum]]
    else:
        sorted_solutions = [final_labels[0]]

    post_min_time = time.time()

    if args.time == 0 or args.time >= 2:
        print("Minimization by {0}: {1:.5f} s".format(args.optmode, post_min_time-pre_min_time))

    if args.time == 0 or args.time >= 1:
        print("Total time: {0:.5f} s".format(post_min_time-start_time))

    if args.verbose == 0 or args.verbose >= 1:
        print("Solutions minimized by {0}".format(args.optmode))
    for idx,ssol in enumerate(sorted_solutions):
        print("SOLUTION #{0}".format(idx))
        print(labels_to_rules(ssol))

if __name__ == "__main__":
    main()
