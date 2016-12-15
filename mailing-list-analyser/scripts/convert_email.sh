#!/bin/bash
sed -i '/^From/s/\b a \b/@/g' ../../testdata/wireless-12-2016.txt
