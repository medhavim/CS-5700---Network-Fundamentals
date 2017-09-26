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

## CBR Rate from 1 to 6
for i in 1 2 3 4 5 6;
do

### Due to space constraints on the server we generated our trace files one after the other
   # python test.py Tahoe1_$i.tr $i Tahoe $1
   # python test.py Reno1_$i.tr $i Reno $1 
     python test.py Newreno1_$i.tr $i Newreno $1
     python test.py Vegas1_$i.tr $i Vegas $1
done

## CBR Rate from 6.1, 6.2, ... 10
for x in $(seq 6.1 0.1 10) ;
do
### Due to space constraints on the server we generated our trace files one after the other
   # python test.py Tahoe1_$x.tr $x Tahoe $1
   # python test.py Reno1_$x.tr $x Reno $1 
     python test.py Newreno1_$x.tr $x Newreno $1
     python test.py Vegas1_$x.tr $x Vegas $1
done
