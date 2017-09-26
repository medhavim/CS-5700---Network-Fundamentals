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
for i in 1 2 3 4 5 6 ;
do
		### Due to space constraints on the server we generated our trace files one after the other

     #python test.py NewrenoReno_$i.tr $i NewrenoReno $1
     #python test.py RenoReno_$i.tr $i RenoReno $1
     python test.py VegasVegas_$i.tr $i VegasVegas $1
     python test.py NewrenoVegas_$i.tr $i NewrenoVegas $1
done

## CBR Rate from 6.1, 6.2, ... 10
for x in $(seq 6.1 0.1 10) ;
do
		### Due to space constraints on the server we generated our trace files one after the other

     #python test.py NewrenoReno_$x.tr $x NewrenoReno $1
     #python test.py RenoReno_$x.tr $x RenoReno $1
     python test.py VegasVegas_$x.tr $x VegasVegas $1
     python test.py NewrenoVegas_$x.tr $x NewrenoVegas $1
done
