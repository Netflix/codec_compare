#!/usr/bin/env python
import sys
import os
import subprocess

img_enc = sys.argv[1]
img_dec = sys.argv[2]
width   = sys.argv[3]
height  = sys.argv[4]
pix_fmt = sys.argv[5]

jpg_bin  = '/tools/jpeg/jpeg'
cmd      = [jpg_bin, img_enc, img_dec]

print " ".join(cmd)
try:
    output = subprocess.check_output(cmd)
except subprocess.CalledProcessError as e:
    print e.output
    sys.exit(1)
