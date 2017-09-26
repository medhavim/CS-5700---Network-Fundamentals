#!/bin/bash

###################################################################################################
## File: run.sh
## Purpose: This is the file that generates the trace files for the different TCP variants
## like Tahoe, Reno, New Reno and Vegas
## Arguements: The arguements given to the tcl file are the TCP Variant, CBR Rate, 
## start time for CBR and TCP and end time for CBR and TCP
## Description: We calculate
###################################################################################################

## Removing the previous generated tr and tcp files
rm *.tr *.tcp

for x in $(seq 2 1 30);

do
### Due to space constraints on the server we generated our trace files one after the other

#/course/cs4700f12/ns-allinone-2.35/bin/ns ./experiment_reno3.tcl -tclargs DropTail $x
#/course/cs4700f12/ns-allinone-2.35/bin/ns ./experiment_sack3.tcl -tclarfs RED $x
/course/cs4700f12/ns-allinone-2.35/bin/ns ./experiment_reno3.tcl -tclargs RED $x
#/course/cs4700f12/ns-allinone-2.35/bin/ns ./experiment_sack3.tcl -tclargs DropTail $x

done

# Parse the trace files  
sh py_parse.sh 1.0
