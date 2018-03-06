#!/bin/bash

#a=0

#while [ true ]
#do
#	printf "num: $a\n"
#	a=$((a + 1))
#	sleep 1
#done
while [ true ]
do
	ssh $1 ls
done