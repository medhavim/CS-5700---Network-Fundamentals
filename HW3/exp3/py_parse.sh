#!/bin/bash

###################################################################################################
## File: py_parse.sh
## Purpose: This is the file that parses the trace files for the different TCP variants
## like Tahoe, Reno, New Reno and Vegas
## Arguements: The arguements given to the python file are the trace file, CBR Rate, TCP Variant, 
## start time 
## Description: This is an intermediary script that provides the parsing python script with 
## the necessary files
###################################################################################################

## Removing the previous generated output files
rm output*.txt

for i in $(seq 2 1 30);
do
### Due to space constraints on the server we generated our trace files one after the other

#python test.py Reno_DropTail.tr Reno_DropTail $1 $i 
python test.py Reno_RED_$i.tr Reno_RED_$i $1 $i Reno_RED
#python test.py Sack1_DropTail_$i.tr Sack1_DropTail_$i $1 $i Sack1_DropTail
#python test.py Sack1_RED_$i.tr Sack1_RED_$i $1 $i Sack1_RED
done
