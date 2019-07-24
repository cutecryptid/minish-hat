import argparse
import clingo
import re
import sys
import time
import copy
import math
from itertools import product, combinations, groupby

def rule_to_label(rulevalues, atoms):
    lb = ""
    for atom in sorted(atoms):
        if not atom in rulevalues['atoms']:
            lb += "x"
        else:
            if atom in rulevalues['phead'] and atom in rulevalues['nhead']:
                lb += '1'
            elif atom in rulevalues['phead']:
                lb += 'z'
            elif atom in rulevalues['nhead']:
                lb += 'o'
            elif atom in rulevalues['pbody']:
                lb += '2'
            elif atom in rulevalues['nbody']:
                lb += '0'
    return lb

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

def get_countermodels(label):
    options = {
        'z': ['0','1'],
        'o': ['1', '2'],
        'x': ['0', '1', '2']
    }
    combos = [(c,) if c not in options else options[c] for c in label]
    return (label_to_octal(''.join(o)) for o in product(*combos))

def get_adjval(octx):
    weight = { 1: 1, 2: 0, 4: 1,
                3: 2, 6: 3, 7: 6 }
    sum = 0
    while octx:
        sum += weight[octx & 7]
        octx >>= 3
    return sum

def get_weight(octx):
    weight = { 1: 0, 2: 0, 4: 0,
                3: 1, 6: 1, 7: 2 }
    sum = 0
    while octx:
        sum += weight[octx & 7]
        octx >>= 3
    return sum

def is_total(octx):
    weight = { 1: 0, 2: 0, 4: 1,
                3: 1, 6: 1, 7: 1 }
    sum = 0
    while octx:
        sum += weight[octx & 7]
        octx >>= 3
    return (sum)

def get_totalize(label):
    options = {
        '2': ['1','2']
    }
    combos = [(c,) if c not in options else options[c] for c in label]
    return (label_to_octal(''.join(o)) for o in product(*combos))

def check_partial_adj(p0, p1):
    or_ret = p0 | p1
    and_ret = p0 & p1
    xor_ret = p0 ^ p1
    ret = 0
    a = p0
    b = p1
    eq_count = 0
    adj_count = 0
    comp_count = 0
    oct_len = max(len(oct(a)), len(oct(b))) - 2
    while a or b or and_ret:
        if (a & 7 == b & 7):
            eq_count += 1
        elif ((b & 7 == and_ret & 7) and (a & 7 == or_ret & 7)):
            comp_count += 1
        elif ((and_ret & 7 == 0) and (xor_ret & 7 != 5)):
            adj_count += 1
        elif ((and_ret & 7 == 2) and (or_ret & 7 == 7) and (xor_ret & 7 == 5)):
            adj_count += 1
        or_ret >>= 3
        xor_ret >>= 3
        and_ret >>= 3
        a >>= 3
        b >>= 3
    return (comp_count >= 1) and (adj_count == 1) and (comp_count + eq_count + adj_count == oct_len)

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
    if count_fives == 0 and count_set == 1 and (octx != res and octy != res):
        dict['is_valid'] = True
        dict['change_pos'] = -1 * len(oct(ret_xor)[2:])
        dict['oct_val'] = res
    return dict

def check_simpler(octx, octy):
    res = octx | octy
    ret_xor = octx ^ octy
    print(octal_to_label(octx), octal_to_label(octy), oct(ret_xor))

    return False

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

def rules_to_string(rule_dict):
    terms = []
    for rk,rv in rule_dict.items():
        termh = ""
        termb = ""
        if len(rv['phead']) + len(rv['nhead']) > 0:
            phead = list(rv['phead'])
            nhead = [ "not " + x for x in list(rv['nhead'])]
            termh += " v ".join(phead + nhead)
        if len(rv['pbody']) + len(rv['nbody']) > 0:
            pbody = list(rv['pbody'])
            nbody = [ "not " + x for x in list(rv['nbody'])]
            termb += ":- " + " ^ ".join(pbody + nbody)
        if len(termh) > 0 and len(termb) > 0:
            termh += " "
        terms += [ termh + termb + "."]
    return "\n".join(terms)

def label_to_ruledict(label, atomset=[]):
    pheadset, nheadset = set(), set()
    pbodyset, nbodyset = set(), set()
    ruleatomset = set()
    for idx,val in enumerate(label):
        if len(atomset) == 0:
            atom = "x" + str(len(label)-idx-1)
        else:
            atom = atomset[idx]
        if val == '0':
            nbodyset.add(atom)
        elif val =='1':
            pheadset.add(atom)
            nheadset.add(atom)
        elif val == '2':
            pbodyset.add(atom)
        elif val == 'o':
            nheadset.add(atom)
        elif val == 'z':
            pheadset.add(atom)
        if val != 'x':
            ruleatomset.add(atom)
    return ({
        'atoms' : ruleatomset,
        'phead' : pheadset,
        'nhead' : nheadset,
        'pbody' : pbodyset,
        'nbody' : nbodyset
    })

def cover_table(cover_dict):
    coveredby = [p['covered_by'] for p in cover_dict.values()]
    primes = set()
    for c in coveredby:
        primes |= set(c)
    primelb = [ octal_to_label(p) for p in sorted(primes) ]
    width = len(primelb[0])
    tablestr = " "*width + "  "
    for lb in primelb:
        tablestr += lb + "  "
    tablestr += "\n"
    for k in sorted(cover_dict.keys()):
        tablestr += octal_to_label(k) + "  "
        for p in sorted(primes):
            if p in cover_dict[k]['covered_by']:
                tablestr += " "*(width//2) + "x"
                if width%2:
                    tablestr += " "*(width//2)
                else:
                    tablestr += " "*((width//2)-1)
                tablestr += "  "
            else:
                tablestr += " "*width + "  "
        tablestr += "\n"
    return tablestr

def rules_to_asp(rule_dict, program_number):
    asp = "program({0}).\n".format(program_number)
    for rk, rv in rule_dict.items():
        asp += "rule({0}, {1}). ".format(program_number, rk)
        for atom in rv['phead']:
            asp += "phead({0}, {1}, '{2}'). ".format(program_number, rk, atom)
        for atom in rv['nhead']:
            asp += "nhead({0}, {1}, '{2}'). ".format(program_number, rk, atom)
        for atom in rv['pbody']:
            asp += "pbody({0}, {1}, '{2}'). ".format(program_number, rk, atom)
        for atom in rv['nbody']:
            asp += "nbody({0}, {1}, '{2}'). ".format(program_number, rk, atom)
        asp += "\n"
    return asp

def main(arguments):
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
    parser.add_argument('-te', '--testeq', action='store_true', default=False,
                        help="Perform Strong Equivalence tests on minimal results")
    parser.add_argument('-ts', '--testsub', action='store_true', default=False,
                        help="Perform Subsumption tests on minimal results")
    parser.add_argument('-ct', '--covertable', action='store_true', default=False,
                        help="Prints Prime Implicate Cover table")
    parser.add_argument('-vt', '--verbosetests', action='store_true', default=False,
                        help="Makes Test Output more verbose")
    args = parser.parse_args(arguments)

    try:
        input_content = args.file.read()
    except Exception as exc:
        print("error parsing file:", args.file.name)
        print(exc)
        return 1

    labels = []
    atoms = set()
    have_cms = False
    have_aggr = False
    have_rules = False
    rule_dict = {}
    rulecount = 1
    explicit_atoms = set()

    for line in input_content.split('\n'):
        m = line.strip()
        atomset = set()
        pheadset, nheadset = set(), set()
        pbodyset, nbodyset = set(), set()
        addrule = False
        if re.match('^\/\w+\/$', m):
            explicit_atoms = set(m[1:-1])
        if re.match('^[012ozx]+$', m) and not have_rules:
            addrule = True
            have_cms = True
            labels += [ m ]
            rule = label_to_ruledict(m, atomset=sorted(explicit_atoms))
        if re.match('^[\w;\s]*(?::-)?[\s\w,]*\.$', m) and not have_cms:
            addrule = True
            have_rules = True
            parts = line.replace('.', '').split(':-')
            for hatom in parts[0].split(';'):
                if len(hatom) > 0:
                    ha = hatom.strip()
                    nots = ha.count("not")
                    if nots == 0:
                        pheadset.add(ha)
                    else:
                        ha = ha.replace('not', '').strip()
                        if nots == 1:
                            nheadset.add(ha)
                        elif nots == 2:
                            nbodyset.add(ha)
                        elif nots > 2:
                            if nots % 2:
                                nheadset.add(ha)
                            else:
                                nbodyset.add(ha)
                    atomset.add(ha)
                if len(parts) > 1:
                    for batom in parts[1].split(','):
                        if len(batom) > 0:
                            ba = batom.strip()
                            nots = ba.count("not")
                            if nots == 0:
                                pbodyset.add(ba)
                            else:
                                ba = ba.replace('not', '').strip()
                                if nots == 1:
                                    nbodyset.add(ba)
                                elif nots == 2:
                                    nheadset.add(ba)
                                elif nots > 2:
                                    if nots % 2:
                                        nbodyset.add(ba)
                                    else:
                                        nheadset.add(ba)
                            atomset.add(ba)
                for atom in sorted(atomset):
                    if ((atom in pheadset and atom in pbodyset) or
                        (atom in nheadset and atom in nbodyset)):
                        try:
                            atomset.remove(atom)
                            pheadset.remove(atom)
                            pbodyset.remove(atom)
                            nheadset.remove(atom)
                            nbodyset.remove(atom)
                        except:
                            pass
                        if len(atomset) == 0:
                            addrule = False
                    if ((atom in pheadset and atom in nbodyset) or
                        (atom in nheadset and atom in pbodyset)):
                            addrule = False
                rule = {
                    'atoms' : atomset,
                    'phead' : pheadset,
                    'nhead' : nheadset,
                    'pbody' : pbodyset,
                    'nbody' : nbodyset
                }
        if addrule:
            rule_dict.update({ rulecount : rule })
            atoms |= atomset
            rulecount += 1

    if len(explicit_atoms) > 0 and not have_rules:
        atoms = explicit_atoms

    if have_rules:
        for rk, rv in rule_dict.items():
            m = rule_to_label(rv, atoms)
            labels += [ m ]

    labelcount = len(labels)

    minterm_dict = {}
    for m in labels:
        id = label_to_octal(m)
        if get_weight(id) > 0:
            have_aggr = True
            covers = list(get_countermodels(m))
        else:
            covers = [id]
        totalcovers = []
        for c in covers:
            if is_total(c):
                label = octal_to_label(c)
                totalcovers += list(get_totalize(label))
        minterm_dict.update({ id : { 'marked': False,
                         'adjval' : get_adjval(id),
                         'covers' : set(covers),
                         'totalcovers' : set(covers+totalcovers)
                         } })

    initial_minterms =  dict()
    for mk, mv in minterm_dict.items():
        for c in mv['covers']:
            id = c
            covers = [c]
            totalcovers = []
            if is_total(c):
                lb = octal_to_label(c)
                totalcovers = list(get_totalize(lb))
            initial_minterms.update({
                id : { 'totalcovers' : set(covers+totalcovers)}
            })

    if args.time:
        pre_pair_loop = time.time()
    adj_count = 1
    exp_count = 1
    step = 0
    while (adj_count+exp_count) > 0:
        exp_count = 0
        adj_count = 0
        if have_aggr:
            delete_list = []
            minkeys = [ k for k,v in minterm_dict.items() if not v['marked']]
            for k1,k2 in combinations(minkeys,2):
                partial = check_partial_adj(k1,k2)
                if partial:
                    expanded = set()
                    if get_weight(k1) > 0:
                        expanded |= minterm_dict[k1]['covers']
                    if get_weight(k2) > 0:
                        expanded |= minterm_dict[k2]['covers']
                    expanded_list = list(expanded)
                    for ek in expanded_list:
                        new_add = 0
                        if not ek in minterm_dict.keys():
                            new_add += 1
                            totalcovers = []
                            if is_total(ek):
                                label = octal_to_label(ek)
                                totalcovers = list(get_totalize(label))
                            minterm_dict.update({ ek : { 'marked': False,
                                             'adjval' : get_adjval(ek),
                                             'covers' : set([ek]),
                                             'totalcovers' : set([ek] + totalcovers) } })
                        if new_add > 0:
                            if get_weight(k1) > 0:
                                delete_list += [k1]
                            if get_weight(k2) > 0:
                                delete_list += [k2]
                        exp_count += new_add

            for k in delete_list:
                minterm_dict.pop(k, None)

        somerules = True
        if len(minterm_dict.keys()) == 0:
            print("Program has no fundamental rules")
            somerules = False
            break

        #TODO: Fix Adj value since now (z, 2) and (o, 0)
        adjval_dict = { }
        for k,v in minterm_dict.items():
            if not v['marked']:
                keyadjval = get_adjval(k)
                if not keyadjval in adjval_dict.keys():
                    adjval_dict.update({ keyadjval : [ k ] })
                else:
                    adjval_dict[keyadjval] += [ k ]

        sorted_adjval = sorted(adjval_dict)
        len_sorted_adjval = len(adjval_dict)-1

        valid_pairs = []
        for (p0, p1) in product(sorted_adjval, repeat=2):
            dif = p1 - p0
            if dif > 0 and dif < 3:
                valid_pairs += [(p0,p1)]

        for (l,r) in valid_pairs:
            leftminterms = adjval_dict[l]
            rightminterms = adjval_dict[r]

            for p0, p1 in product(leftminterms, rightminterms):
                adj = check_adjacent(p0, p1)
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
                        if oct(p0)[adj['change_pos']] == '2':
                            minterm_dict[p0]['marked'] = True
                        if oct(p1)[adj['change_pos']] == '2':
                            minterm_dict[p1]['marked'] = True
                    adj_count += 1
                    if not result in minterm_dict.keys():
                        newcovers = set.union(minterm_dict[p0]['covers'],
                                        minterm_dict[p1]['covers'])
                        newtotalcovers = set.union(minterm_dict[p0]['totalcovers'],
                                        minterm_dict[p1]['totalcovers'])
                        minterm_dict.update({ result: { 'marked' : False,
                                'adjval' : get_adjval(result),
                                'covers' : newcovers,
                                'totalcovers' : newtotalcovers } })
        step += 1

    if somerules:
        if args.time:
            post_pair_loop = time.time()
            print("Pair Time: {0:.5f} s".format(post_pair_loop-pre_pair_loop))
            pre_essential = time.time()

        unmarked = { k: dict(v, **{ 'is_essential' : False }) for k, v in minterm_dict.items() if not v['marked'] }

        cover_dict = dict()
        for ik, iv in initial_minterms.items():
            for uk, uv in unmarked.items():
                if ik in uv['covers']:
                    if not ik in cover_dict.keys():
                        cover_dict.update( { ik: { 'covered_by' : [ uk ],
                                    'is_used' : False } } )
                    else:
                        cover_dict[ik]['covered_by'] += [ uk ]

        if args.covertable:
            print("COVER TABLE")
            print(cover_table(cover_dict))

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
                            essential_cover = unmarked[ek]['totalcovers']
                            essential_implicates.update({ ek : { 'totalcovers': essential_cover } })
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
                limited_cover = set(v['totalcovers']) & minids
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

            #print("Minimizing Solutions by minimal number of {0}".format(args.minmode))
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
            print("")

        atomfacts = ""
        for a in sorted(atoms):
            atomfacts += "sigatom('{0}'). ".format(a)
        base_program = rules_to_asp(rule_dict, 1)
        if args.testeq:
            models_p1 = solve('test_models', [base_program, atomfacts], ["0"])
            models_p1 = [sorted(m) for m in models_p1]
        print("Optimal Minimal Solutions: {0}".format(minsolcount))
        acum_error_smaller = 0
        acum_error_noteq = 0
        acum_warning_smaller = 0
        initial_labels = labels
        for idx,sol in enumerate(selected_solutions):
            print("MINIMAL SOLUTION #{0}".format(idx))
            labels = []
            rules = dict()
            for id in sol:
                labels += [ octal_to_label(int(id))]
            for jdx,lb in enumerate(labels):
                rules.update({jdx+1 : label_to_ruledict(lb, atomset=sorted(atoms))})
            min_program = rules_to_asp(rules, idx+2)
            print(rules_to_string(rules))
            if args.testsub:
                cnt, notsuper = 0, 0
                test_sol = solve('test_subprogram', [base_program, min_program], [])
                for sym in test_sol[0]:
                    if sym.name == 'cntrules':
                        cnt += 1
                        cntargs = sym.arguments
                        if args.verbosetests:
                            print("RULE {0} subsums BASE PROGRAM'S RULE {1}".format(cntargs[1].number, cntargs[3].number))
                    elif sym.name == 'notsuper':
                        notsuper += 1
                        notsuperargs = sym.arguments
                        if args.verbosetests:
                            print("RULE {0} doesn't subsum any rule of P1".format(notsuperargs[1].number))
                if notsuper == 0:
                    print("[SUBSUM TEST] OK")
                else:
                    suberror = False
                    warned = False
                    notsimpler = 0
                    # Check that the rulecount is the same and not greater, at least
                    # the program is sintactically simpler to give it a soft pass
                    simpler_test_sol = solve('test_simpler', [base_program, min_program], [])
                    for sym in simpler_test_sol[0]:
                        if sym.name == 'cntrules':
                            cnt += 1
                            cntargs = sym.arguments
                        elif sym.name == 'notsuper':
                            notsimpler += 1
                            notsuperargs = sym.arguments
                        if notsimpler == 0:
                            warned = True
                        else:
                            suberror = True
                    if suberror:
                        print("[SUBSUM TEST] ERROR")
                        acum_error_smaller += 1
                    elif warned:
                        print("[SUBSUM TEST] WARNING: Program is equal in size, but sintactically simpler")
                        acum_warning_smaller += 1
            if args.testeq:
                models_pmin = solve('test_models', [min_program, atomfacts], ["0"])
                models_pmin = [sorted(m) for m in models_pmin]
                partcount = 0
                for m in models_p1:
                    if args.verbosetests:
                        if m in models_pmin:
                            print("MODEL {0} is also in the minimal program models".format(m))
                        else:
                            print("MODEL {0} is not in the minimal program models".format(m))
                        partcount += 1
                for m in models_pmin:
                    if args.verbosetests:
                        if m in models_p1:
                            print("MODEL {0} is also in the original program models".format(m))
                        else:
                            print("MODEL {0} is not in the original program models".format(m))
                        partcount += 1
                if partcount == 0:
                    print("[STRONG EQ TEST] OK")
                else:
                    print("[STRONG EQ TEST] ERROR")
                    acum_error_noteq += 1
        if args.testsub:
            if acum_error_smaller == 0:
                if acum_warning_smaller == 0:
                    print("[TEST RESULT] All solutions are smaller")
                else:
                    print("[TEST RESULT] All solutions are smaller or equal but sintactically simpler")
            else:
                print("[TEST RESULT] There are {0} solutions that are not smaller".format(acum_error_smaller))
        if args.testeq:
            if acum_error_noteq == 0:
                print("[TEST RESULT] All solutions are strongly equivalent")
            else:
                print("[TEST RESULT] There are {0} solutions that are not strongly equivalent".format(acum_error_noteq))
        statsdict = {
            "errorsub" : acum_error_smaller,
            "erroreq"  : acum_error_noteq,
            "atoms"    : len(atoms),
            "rules"    : labelcount,
            "time"     : post_min-pre_pair_loop,
        }
        return statsdict

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
