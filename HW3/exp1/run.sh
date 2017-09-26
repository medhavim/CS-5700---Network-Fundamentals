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

## For CBR Rate 1 to 6
for i in 1 2 3 4 5 6 ;
do
	### Due to space constraints on the server we generated our trace files one after the other

	#/course/cs4700f12/ns-allinone-2.35/bin/ns ./experiment_tahoe1.tcl -tclargs $i
	#/course/cs4700f12/ns-allinone-2.35/bin/ns ./experiment1.tcl -tclargs Reno $i 3.0 1.0 4.0 6.0 
	/course/cs4700f12/ns-allinone-2.35/bin/ns ./experiment1.tcl -tclargs Newreno $i 3.0 1.0 4.0 6.0
	/course/cs4700f12/ns-allinone-2.35/bin/ns ./experiment1.tcl -tclargs Vegas $i 3.0 1.0 4.0 6.0
done

## For CBR Rate 6.1, 6.2, ... , 10
for x in $(seq 6.1 0.1 10) ;
do
	### Due to space constraints on the server we generated our trace files one after the other

	#/course/cs499700f12/ns-allinone-2.35/bin/ns ./experiment_tahoe1.tcl -tclargs $x
	#/course/cs4700f12/ns-allinone-2.35/bin/ns ./experiment1.tcl -tclargs Reno $x 3.0 1.0 4.0 6.0
	/course/cs4700f12/ns-allinone-2.35/bin/ns ./experiment1.tcl -tclargs Newreno $x 3.0 1.0 4.0 6.0
	/course/cs4700f12/ns-allinone-2.35/bin/ns ./experiment1.tcl -tclargs Vegas $x 3.0 1.0 4.0 6.0
done

# Parse the trace files 
sh py_parse.sh 1.0
