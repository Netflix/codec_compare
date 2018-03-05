#!/usr/bin/env python
import sys
import os
import subprocess
import shutil
import glob

img_enc = sys.argv[1]
img_dec = sys.argv[2]
width   = sys.argv[3]
height  = sys.argv[4]
pix_fmt = sys.argv[5]

if pix_fmt == "ppm":
    kakadu_bin = '/tools/kakadu/KDU7A2_Demo_Apps_for_Ubuntu-x86-64_170827/kdu_expand'
if pix_fmt == "yuv420p":
    in_tmp = '/tmp/kakadu.mj2'
    shutil.copyfile(img_enc, in_tmp)
    img_enc = in_tmp
    kakadu_bin = '/tools/kakadu/KDU7A2_Demo_Apps_for_Ubuntu-x86-64_170827/kdu_v_expand'

cmd = [kakadu_bin, "-i", img_enc, "-o", img_dec]
print " ".join(cmd)
try:
    output = subprocess.check_output(cmd)
    if pix_fmt == "yuv420p":
        file_out = glob.glob('%s*' % (os.path.splitext(img_dec)[0]))[0]
        os.rename(file_out, img_dec)
except subprocess.CalledProcessError as e:
    print e.output
    sys.exit(1)
