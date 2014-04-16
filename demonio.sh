#!/bin/bash
proceso="/root/at-5000/at-5000.py"
pid=`ps auxw | grep $proceso | grep -v grep`
if [ -z "$pid" ]; then
	echo "AT-5000 caido. Levantando..."
	/root/at-5000/at-5000.py start &
fi

