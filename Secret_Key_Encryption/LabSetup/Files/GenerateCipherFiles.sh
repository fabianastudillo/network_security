#!/bin/bash
#
# Script Name: GenerateCipherFiles.sh
# Description: This files generate a different cipher file for each group in the
#              Network Security course of the University of Cuenca.
# Usage:       ./GenerateCipherFiles.sh
#              Example: ./GenerateCipherFiles.sh
# Author:      Your Name
# Date:        2024-10-24
# Version:     1.0
# License:     MIT License
#
#
# Exit Status:
#  0  : Success
#  >0 : Failure
#

year="sep-2024"
number_of_groups=10

for i in $(seq 1 $number_of_groups);
do
    clave=`echo {a..z} | sed 's/ /\n/g' | shuf | tr '\n' ' ' | sed 's/ //g'`
    #clave=`awk NR==1 claves-Sep2024.txt`
    tr [:upper:] [:lower:] < textoclaro-Sep2024.txt > textoclaro-Sep2024-lower.txt
    tr -cd '[a-z][\n][:space:]' < textoclaro-Sep2024-lower.txt > plaintext.txt
    tr 'a-z' $clave < plaintext.txt > "textoCifradoGrupo${i}.bin"
    echo "$clave" >> "claves-${year}.txt"
done