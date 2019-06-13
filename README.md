# Minish HAT: Here-And-There Logic Program and Theories minimization in ASP

## Usage
Run ```python minish-countermodels.py INPUT_FILE```. Python 3.x and clingo 5.x.
Asprin is optional but recommended, as it is just used for complex minimization modes.

The input file must contain the terms of the function to minimize in their ternary representation, one term per line. See the samples at the provided input folder for reference. These terms should be either the countermodels of the logic program/theory or the program rules translated to labels (with ```z=not 2``` and ```o=not 0```).

The script generates the prime implicates in Python and leverages ASP to do the mincover for all of the generated prime implicates. This behaviour can be altered to let python extract the Essential Implicates first and use ASP to determine the remaining minimal coverage by using the parameter ```-hc/--hybridcover```.

Only a single minimal solution will be specified, to show all of the possible minimal solutions, use the ```--all``` parameter. Minimization method can be specified through the ```-m / --minmode``` parameter.

### Usage Output
```
usage: minish-countermodels.py [-h] [-hc] [-a] [-m {atoms,terms}] [-t] [file]

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
```

## TO DO
* Input file should be a logic program or theory.
* Only simple minimizations by atoms and terms are supported, no asprin option to combine or minimal subset yet.
* Combine CMs and Ruleset scripts by checking input file
