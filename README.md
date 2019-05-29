# Quine-McCluskey-Petrick in ASP for Here-And-There

## Usage
Run ```python minterms.py INPUT_FILE```. Python 3.x and clingo 5.x and asprin are required.

There is an hybrid implementation that leverages ASP for the minimal coverage and performs the pairing with python, you can try it using ```bitwise-minterms.py``` instead. Input files are the same for both scripts.

The input file must contain the terms of the function to minimize in their ternary representation, one term per line. See the samples at the provided input folder for reference.

The script will show the prime implicants for the provided minterms, extract the essential implicants and process the remaining implicants to achieve total coverage. Only a single minimal solution will be specified, to show all of the possible minimal solutions, use the ```--all``` parameter. Minimization method can be specified through the ```-m / --minmode``` parameter.

## TO DO
* Input file should be a logic program?
* Only works with countermodels input, either calculate countermodels for a logic program or work with
the direct translation of the rules.
