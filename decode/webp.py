#!/usr/bin/env python
import sys
import os
import subprocess

# Usage: dwebp in_file [options] [-o out_file]
img_enc  = sys.argv[1]
img_dec  = sys.argv[2]

webp_bin = '/tools/libwebp-0.6.1-linux-x86-64/bin/dwebp'
cmd      = [webp_bin, img_enc, "-ppm", "-o", img_dec]

print " ".join(cmd)
try:
    output = subprocess.check_output(cmd)
except subprocess.CalledProcessError as e:
    print e.output
    sys.exit(1)
