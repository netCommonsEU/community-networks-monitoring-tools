#!/bin/bash
sed '/^From/s/\b a \b/@/g' ../../testdata/wireless-12-2016.txt > ../../testdata/wireless-12-2016-converted.txt 
