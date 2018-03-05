#!/usr/bin/env python
import sys
import os
import subprocess
import math

image_src  = sys.argv[1]
image_out  = sys.argv[2]
bpp_target = sys.argv[3]
width      = sys.argv[4]
height     = sys.argv[5]
pix_fmt    = sys.argv[6]
depth      = sys.argv[7]

if depth != "8":
    print "8 bit only"
    sys.exit(1)

jpg_bin = '/tools/jpeg/jpeg'

print pix_fmt

if pix_fmt == "ppm" or pix_fmt == "yuv444p":
    subsampling = "1x1,1x1,1x1"
elif pix_fmt == "yuv422p":
    image_src = image_src.replace("/yuv422p/", "/ppm/")
    subsampling = "1x1,2x1,2x1"
elif pix_fmt == "yuv420p":
    subsampling = "1x1,2x2,2x2"
    image_src = image_src.replace("/yuv420p/", "/ppm/").replace(".yuv", ".ppm")

qty_min, qty_max = 0, 100
quality = qty_max / 2
step = quality / 2

for i in range(0, int(math.floor(math.log(qty_max)/math.log(2)))):
    cmd = [jpg_bin, '-q', str(quality), '-s', subsampling, image_src, image_out]
    print " ".join(cmd)
    try:
        output = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        print e.output
        sys.exit(1)

    size = os.path.getsize(image_out) * 8
    bpp  = float(size) / float((int(width) * int(height)))
    print quality, step, size, bpp, bpp_target

    quality += step * (1 if (bpp < float(bpp_target)) else -1)
    step /= 2

print output
