#!/bin/bash
for i in {0..13}
do
	sudo trace-cmd report -t --cpu $i >cpu$i
done

