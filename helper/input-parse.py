import argparse
import sys

def rule_to_label(rulevalues, atoms):
    lb = ""
    for atom in sorted(atoms):
        if not atom in rulevalues['atoms']:
            lb += "x"
        else:
            if atom in rulevalues['phead'] and rulevalues['nhead']:
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


def main():
    parser = argparse.ArgumentParser(description='Here-And-There Logic Program and Theories minimization in ASP')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin, help="Logic Program File (default: stdin)")
    args = parser.parse_args()

    try:
        logic_program = args.file.read()
    except Exception as exc:
        print("error parsing file:", args.file.name)
        print(exc)
        return 1

    atoms = set()
    rule_dict = {}
    rulecount = 1
    for line in logic_program.split('\n'):
        if len(line) > 0 and not '%' in line:
            atomset = set()
            pheadset, nheadset = set(), set()
            pbodyset, nbodyset = set(), set()
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
                addrule = True
                for atom in sorted(atomset):
                    if ((atom in pheadset and atom in pbodyset) or
                        (atom in nheadset and atom in nbodyset)):
                        atomset.remove(atom)
                        pheadset.remove(atom)
                        pbodyset.remove(atom)
                        nheadset.remove(atom)
                        nbodyset.remove(atom)
                        print("Removing atom {0} from rule {1}".format(atom, rulecount))
                        if len(atomset) == 0:
                            addrule = False
                            print("Rule {0} has become empty".format(rulecount))
                    if ((atom in pheadset and atom in nbodyset) or
                        (atom in nheadset and atom in pbodyset)):
                            addrule = False
                            print("Rule {0} is inconsistent".format(rulecount))
                if addrule:
                    rule_dict.update({ rulecount : {
                        'atoms' : atomset,
                        'phead' : pheadset,
                        'nhead' : nheadset,
                        'pbody' : pbodyset,
                        'nbody' : nbodyset
                    }})
                    atoms |= atomset
                    rulecount += 1

    for rk, rv in rule_dict.items():
        print(rk, rule_to_label(rv, atoms))

if __name__ == "__main__":
    main()
