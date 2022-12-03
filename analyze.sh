#!/bin/bash
for((i=0;i<10;i++))
do
	sudo trace-cmd report -t --cpu $i > cpu$i
done



