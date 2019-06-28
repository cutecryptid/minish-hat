# Minish HAT: Here-And-There Logic Program and Theories minimization in ASP

## Usage
Run ```python minish-hat.py INPUT_FILE```. Python 3.x and clingo 5.x.
Asprin is optional but recommended, as it is just used for complex minimization modes.

The input file must contain the terms of the function to minimize either in their ternary representation, one term per line or in a logic program format without nesting.  
In ternary representation, the terms should be either the countermodels of the logic program/theory or the program rules translated to labels (with ```z=not 2``` and ```o=not 0```).  
If not specified, atoms will be named x0..xn with x0 being the rightmost atom. Atoms' names can be specified by adding a single line before the rules between slashes e.g. ```/pq/```.  
In any case, see the samples at the provided input folder for reference.

### Usage Output
```
usage: minish-hat.py [-h] [-hc] [-a] [-m {atoms,terms}] [-t] [-te] [-ts] [-ct]
                     [file]

Here-And-There Logic Program and Theories minimization in ASP

positional arguments:
  file                  TXT File (default: stdin)

optional arguments:
  -h, --help            show this help message and exit
  -hc, --hybridcover    Perform mincover in two steps python-ASP instead of
                        all ASP
  -a, --all             Show all minimal solutions instead of a single one
  -m {atoms,terms}, --minmode {atoms,terms}
                        Minimization method, less atoms by default
  -t, --time            Show time measures for the different stages
  -te, --testeq         Perform Strong Equivalence tests on minimal results
  -ts, --testsub        Perform Subsumption tests on minimal results
  -ct, --covertable     Prints Prime Implicate Cover table
```

## TO DO
* Only simple minimizations by atoms and terms are supported, no asprin option to combine or minimal subset yet.
* Switch mode automatically in the absence of aggregates to perform the vanilla algorithm.
