# FLEXLM_Comsol
Interpreter for FLEXLM license statues inquiries of COMSOL's license daemon.

Application to be ran from terminal, with options for file output.

## Dependencies
Interpreter is written in Python using the following libraries:
 + argparse
 + datetime
 + json
 + numpy
 + os
 + pandas
 + pprint
 + re

User must (independently) provide the following binaries:
 + lmtools
 + lmutil

## Usage Notes
Required license file is directly provided to lmtools

`lic_query = os.popen("lmutil lmstat -a -c " + lic_file).read()`

An example input is included.
