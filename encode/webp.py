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

if pix_fmt != "yuv420p":
    print "WebP is 420 only"
    sys.exit(1)

webp_bin = '/tools/libwebp-0.6.1-linux-x86-64/bin/cwebp'

qty_min, qty_max = 0, 100
quality = qty_max / 2
step = quality / 2

for i in range(0, int(math.floor(math.log(qty_max)/math.log(2)))):
    cmd = [webp_bin, "-m", "6", "-q", str(quality), "-s", width, height, image_src, "-o", image_out]
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
