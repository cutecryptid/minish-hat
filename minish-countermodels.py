import argparse
import clingo
import re
import sys
import time
import copy
from itertools import product

def parse_input(file_contents):
    dict = {}
    for line in file_contents.split('\n'):
        if re.match('^[012ozx]+\s*$', line):
            m = line.strip()
            if re.match('[012ozx]*[zox][012ozx]*', line):
                eids = get_countermodels(m)
            else:
                eids = [label_to_octal(m)]
            for id in eids:
                dict.update({ id : { 'marked': False,
                             'covers' : frozenset([id]) } })
    return dict

def get_countermodels(label):
    options = {
        'z': ['0','1'],
        'o': ['1', '2'],
        'x': ['0', '1', '2']
    }
    combos = [(c,) if c not in options else options[c] for c in label]
    return (label_to_octal(''.join(o)) for o in product(*combos))

def get_totalize(label):
    options = {
        '2': ['1','2']
    }
    combos = [(c,) if c not in options else options[c] for c in label]
    return (label_to_octal(''.join(o)) for o in product(*combos))

def get_adjval(octx):
    weight = { 1: 0, 2: 1, 4: 2,
                3: 4, 6: 5, 7: 7 }
    sum = 0
    while octx:
        sum += weight[octx & 7]
        octx >>= 3
    return sum

def label_to_octal(label):
    translation = {
        '0' : '1',
        '1' : '2',
        '2' : '4',
        'z' : '3',
        'o' : '6',
        'x' : '7',
    }
    octalstr = ""
    for a in label:
        octalstr += translation[a]
    return int(octalstr, 8)

def octal_to_label(octx):
        translation = {
            '1' : '0',
            '2' : '1',
            '4' : '2',
            '3' : 'z',
            '6' : 'o',
            '7' : 'x',
        }
        label = ""
        for a in oct(octx)[2:]:
            label += translation[a]
        return label

def check_adjacent(octx, octy):
    count_set = 0
    count_fives = 0
    res = octx | octy
    ret_xor = octx ^ octy
    res_or = res
    res_xor = ret_xor
    while (res_or and res_xor):
        count_set += 1 if (res_xor & 7 > 0) else 0
        count_fives += 1 if (res_or & 7 == 5) else 0
        res_or >>= 3
        res_xor >>= 3
    dict =  { 'is_valid' : False, 'change_pos': 0, 'oct_val' : None }
    if count_fives == 0 and count_set == 1:
        dict['is_valid'] = True
        dict['change_pos'] = -1 * len(oct(ret_xor)[2:])
        dict['oct_val'] = res
    return dict

def mincover_facts(label_cover_dict):
    facts = ""
    for k,v in label_cover_dict.items():
        facts += "leftid(\"{0}\"). ".format(k)
        for val in v:
            facts += "covers(\"{0}\", \"{1}\"). ".format(k, val)
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

def solve_optimal(asp_program, asp_facts, clingo_args):
    c = clingo.Control(clingo_args + ["--opt-mode=optN"])
    if asp_program != "":
        c.load("./asp/"+asp_program+".lp")
    for facts in asp_facts:
        c.add("base", [], facts)
    c.ground([("base", [])])
    ret = []
    with c.solve(yield_=True) as handle:
        for m in handle:
            if (m.optimality_proven):
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
    parser = argparse.ArgumentParser(description='Here-And-There Logic Program and Theories minimization in ASP')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin, help="TXT File (default: stdin)")
    parser.add_argument('-hc', '--hybridcover', action='store_true', default=False,
                        help="Perform mincover in two steps python-ASP instead of all ASP")
    parser.add_argument('-a', '--all', action='store_true', default=False,
                        help="Show all minimal solutions instead of a single one")
    parser.add_argument('-m', '--minmode', choices=['atoms', 'terms'], default='atoms',
                        help="Minimization method, less atoms by default")
    parser.add_argument('-t', '--time', action='store_true', default=False,
                        help="Show time measures for the different stages")
    args = parser.parse_args()

    try:
        minterm_dict = parse_input(args.file.read())
    except Exception as exc:
        print("error parsing file:", args.file.name)
        print(exc)
        return 1

    for k,v in minterm_dict.items():
        label = octal_to_label(k)
        if re.match(r"^[0,2]+$", label):
            minterm_dict[k]['covers'] = frozenset(list(get_totalize(label)))

    initial_minterms =  copy.deepcopy(minterm_dict)

    if args.time:
        pre_pair_loop = time.time()
    adjval_dict = { }
    for k in minterm_dict.keys():
        keyadjval = get_adjval(k)
        if not keyadjval in adjval_dict.keys():
            adjval_dict.update({ keyadjval : [ k ] })
        else:
            adjval_dict[keyadjval] += [ k ]

    while len(adjval_dict):
        sorted_adjval = sorted(adjval_dict)
        len_sorted_adjval = len(adjval_dict)-1
        new_adjval_dict = {}
        for x in range(len_sorted_adjval):
            if (sorted_adjval[x+1]-sorted_adjval[x]) == 1:
                leftminterms = adjval_dict[sorted_adjval[x]]
                rightminterms = adjval_dict[sorted_adjval[x+1]]
                for left in leftminterms:
                    for right in rightminterms:
                        adj = check_adjacent(left, right)
                        if adj['is_valid']:
                            result = adj['oct_val']
                            keyadjval = get_adjval(result)
                            ch_pos = adj['change_pos']
                            if oct(result)[ch_pos] == '7':
                                lenres = len(oct(result))
                                octmask = '0o' + '7'*(lenres-2)
                                breakpos = lenres + ch_pos
                                octmask = int(octmask[:breakpos] + '0' + octmask[breakpos+1:],8)
                                for k in minterm_dict.keys():
                                    if (octmask & k == octmask & result) and (k != result):
                                        minterm_dict[k]['marked'] = True
                            else:
                                if oct(left)[adj['change_pos']] == '2':
                                    minterm_dict[left]['marked'] = True
                                if oct(right)[adj['change_pos']] == '2':
                                    minterm_dict[right]['marked'] = True
                            if not keyadjval in new_adjval_dict.keys():
                                new_adjval_dict.update({ keyadjval : [ result ] })
                            else:
                                if not result in new_adjval_dict[keyadjval]:
                                    new_adjval_dict[keyadjval] += [ result ]
                            newcovers = frozenset.union(minterm_dict[left]['covers'],
                                            minterm_dict[right]['covers'])
                            minterm_dict.update({ result: { 'marked' : False,
                                    'covers' : newcovers } })
        adjval_dict = new_adjval_dict

    if args.time:
        post_pair_loop = time.time()
        print("Pair Time: {0:.5f} s".format(post_pair_loop-pre_pair_loop))
        pre_essential = time.time()

    unmarked = { k: dict(v, **{ 'is_essential' : False }) for k, v in minterm_dict.items() if not v['marked'] }
    cover_dict = dict()
    for ik, iv in initial_minterms.items():
        for uk, uv in unmarked.items():
            if len(iv['covers'] & uv['covers']):
                if not ik in cover_dict.keys():
                    cover_dict.update( { ik: { 'covered_by' : [ uk ],
                                'is_used' : False } } )
                else:
                    cover_dict[ik]['covered_by'] += [ uk ]

    if args.hybridcover:
        essential_implicates = dict()
        step = 0
        fullcover = False
        initial_minterms_set = frozenset(initial_minterms.keys())
        while True:
            essential_count = 0
            unused_cover_dict = { k : v for k, v in cover_dict.items() if not v['is_used']}
            if len(unused_cover_dict.items()) == 0:
                fullcover = True
                break
            for ck, cv in unused_cover_dict.items():
                if len(cv['covered_by']) == 1:
                    essential_count += 1
                    for ek in cv['covered_by']:
                        essential_cover = unmarked[ek]['covers']
                        essential_implicates.update({ ek : { 'covers': essential_cover } })
                        unmarked[ek]['is_essential'] = True
                        for minid in list(essential_cover & initial_minterms_set):
                            cover_dict[minid]['is_used'] = True
            if essential_count == 0:
                break
            step += 1

        essential_ids = [k for k in essential_implicates.keys()]
        if args.time:
            post_essential = time.time()
            print("Essential Extraction Time: {0:.5f} s".format(post_essential-pre_essential))

    if args.time:
        pre_petrick = time.time()
    if args.hybridcover and fullcover:
        final_ids = [essential_ids]
    else:
        if args.hybridcover:
            prime_left = { k : v for k, v in unmarked.items() if not v['is_essential']}
        else:
            prime_left = unmarked
            unused_cover_dict = cover_dict
        minids = set()
        for k in unused_cover_dict.keys():
            minids.add(k)

        id_cover = {}
        for k,v in prime_left.items():
            limited_cover = set(v['covers']) & minids
            if len(limited_cover) > 0:
                id_cover.update( { k : limited_cover } )

        petrick_facts = mincover_facts(id_cover)
        if args.hybridcover:
            petrick_solutions = solve('petrick_hybrid', [petrick_facts], ["0"])
        else:
            petrick_solutions = solve_optimal('min-cover-full', [petrick_facts], [])
            essential_ids = []
        final_ids = []
        for sol in petrick_solutions:
            selected_ids = []
            for sym in sol:
                if sym.name == "selectid":
                    id = str(sym.arguments[0])[1:-1]
                    selected_ids += [int(id)]
            final_ids += [essential_ids + selected_ids]

    if args.time:
        post_petrick = time.time()
        print("Petrick Time: {0:.5f} s".format(post_petrick-pre_petrick))
        pre_min = time.time()

    if len(final_ids) > 1:
        minimize_facts = ""
        for idx,ids in enumerate(final_ids):
            asp = "solution({0}). ".format(idx)
            for id in ids:
                for x,a in enumerate(octal_to_label(id)):
                    asp += "sol(impl(\"{0}\",x{1},{2}), {3}). ".format(id, x, a, idx)
            minimize_facts += asp

        print("Minimizing Solutions by minimal number of {0}".format(args.minmode))
        minimal_solutions = solve_optimal('less-' +args.minmode, [minimize_facts], [])

        selected_solutions = []
        if not args.all:
            if len(minimal_solutions) > 1:
                minsolcount = "1+"
            minimal_solutions = [minimal_solutions[0]]
        else:
            minsolcount = str(len(minimal_solutions))
        for sol in minimal_solutions:
            for sym in sol:
                if sym.name == "selectsol":
                    selected_solution_id = sym.arguments[0].number
                    selected_solutions += [final_ids[selected_solution_id]]
    else:
        minsolcount = "1"
        selected_solutions = [ final_ids[0] ]

    if args.time:
        post_min = time.time()
        print("Minimal Solution: {0:.5f} s".format(post_min-pre_min))
        print("Total Exec Time: {0:.5f} s".format(post_min-pre_pair_loop))

    print("Optimal Minimal Solutions: {0}".format(minsolcount))
    for idx,sol in enumerate(selected_solutions):
        print("MINIMAL SOLUTION #{0}".format(idx))
        labels = []
        for id in sol:
            labels += [ octal_to_label(int(id))]
        print(labels_to_rules(labels))



if __name__ == "__main__":
    main()
