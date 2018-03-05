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

hevc_bin = '/tools/HM-16.9+SCM-8.0/bin/TAppEncoderStatic'
hevc_cfg = '/tools/HM-16.9+SCM-8.0/cfg/encoder_intra_main_rext.cfg'

if pix_fmt == "ppm":
    chroma_fmt = "444"
    try:
        image_src_gbr = '/tmp/tmp.rgb'
        cmd = ["ffmpeg", "-y", "-i", image_src, "-pix_fmt", "gbrp", image_src_gbr]
        output = subprocess.check_output(cmd)
        image_src = image_src_gbr
    except subprocess.CalledProcessError as e:
        print cmd
        print e.output
        sys.exit(1)
elif pix_fmt == "yuv420p":
    chroma_fmt = "420"


qp_min, qp_max = 0, 51
qp = qp_max / 2
step = qp / 2

for i in range(0, int(math.floor(math.log(qp_max)/math.log(2)))):
    cmd = [hevc_bin, "-c", hevc_cfg, "-f", "1", "-fr", "1", "-q", str(qp), "-wdt", width, "-hgt", height,
           "--InputChromaFormat=%s" % (chroma_fmt), "--ConformanceWindowMode", "1", "-i", image_src, "-b", image_out, "-o", "/dev/null"
          ]
    print " ".join(cmd)
    try:
        output = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        print e.output
        sys.exit(1)

    size = os.path.getsize(image_out) * 8
    bpp  = float(size) / float((int(width) * int(height)))
    print qp, step, size, bpp, bpp_target

    qp += step * (1 if (bpp > float(bpp_target)) else -1)
    step /= 2

print output
