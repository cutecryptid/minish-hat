import os
import argparse
import sys
from minish_hat import main as minimize

def main(arguments):
    parser = argparse.ArgumentParser(description='Minish-HAT but for directories')
    parser.add_argument('directory', type=str, help="Directory containing any type of valid input for minish-HAT")
    parser.add_argument('-o', '--out', type=str, default="minish.log", help="Output File, minish.log by default")
    args = parser.parse_args(arguments)

    orig_stdout = sys.stdout
    outlog = open(args.out, 'w')

    sys.stdout = outlog

    suberror = 0
    suberrorcases = []
    eqerror = 0
    eqerrorcases = []
    timestats = { "nrules" : {}, "natoms" : {} }
    files = [x for x in os.listdir(args.directory) if x.endswith(".lp") or x.endswith(".txt")]
    for i,f in enumerate(files):
        print('-'*40)
        print("[{0}]".format(i) +args.directory + "/" + f + ":")
        print("ORIGINAL FILE:")
        with open(args.directory + "/" + f, 'r') as fin:
            print(fin.read())
        print('-'*40)
        print("MINIMAL PROGRAM:")
        stats = minimize([args.directory + "/" + f, "-te", "-ts", "-t"])
        print('-'*40)
        if stats != None:
            if stats['errorsub'] != 0:
                suberror += 1
                suberrorcases += [i]
            if stats['erroreq'] != 0:
                eqerror += 1
                eqerrorcases += [i]
            if not stats['rules'] in timestats['nrules'].keys():
                timestats['nrules'].update({ stats['rules'] : [stats['time']] })
            else:
                timestats['nrules'][stats['rules']] += [stats['time']]
            if not stats['atoms'] in timestats['natoms'].keys():
                timestats['natoms'].update({ stats['atoms'] : [stats['time']] })
            else:
                timestats['natoms'][stats['atoms']] += [stats['time']]
    nfiles = len(files)

    restr = ""
    restr += '-'*40 + "\n"
    restr += "RESULTS" + "\n"
    restr += '-'*40 + "\n"

    restr += "{0} out of {1} ({2:.2f}%) programs are strongly equivalent\n".format(
                nfiles-eqerror, nfiles, ((nfiles-eqerror)/nfiles)*100)
    if len(eqerrorcases) > 0:
        restr += "Not Strongly Equivalent Cases:\n"
        restr += ", ".join(["[{0}] '{1}'".format(i,files[i]) for i in eqerrorcases]) + "\n"
    restr += "{0} out of {1} ({2:.2f}%) programs are properly smaller\n".format(
                nfiles-suberror, nfiles, ((nfiles-suberror)/nfiles)*100)
    if len(suberrorcases) > 0:
        restr += "Not Properly Smaller Cases:\n"
        restr += ", ".join(["[{0}] '{1}'".format(i,files[i]) for i in suberrorcases]) + "\n"


    print(restr)

    sys.stdout = orig_stdout
    outlog.close()

    print(restr)

    #TODO: Average times for atoms and rules and display somehow
    #      Maybe tables, maybe plot them, maybe export a csv


if __name__ == "__main__":
    main(sys.argv[1:])
