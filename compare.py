#!/usr/bin/env python
import errno
import os
import sys
import subprocess
import json

def mkdir_p(path):
    """ mkdir -p
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def listdir_full_path(directory):
   """ like os.listdir(), but returns full paths
   """
   for f in os.listdir(directory):
       if not os.path.isdir(f):
           yield os.path.abspath(os.path.join(directory, f))

def get_dimensions(image):
    """ given a source image, return dimensions
    """
    try:
        dimension_cmd = ["identify", '-format', '%w,%h,%z', image]
        width, height, depth = subprocess.check_output(dimension_cmd).split(",")
    except subprocess.CalledProcessError as e:
        print dimension_cmd, e.output
    return width, height, depth

def encode(encoder, bpp_target, image, width, height, pix_fmt, depth):
    """ given a encoding script and a test image:
        encode image for each bpp target and place it in the ./output directory 
    """
    encoder_name = os.path.splitext(encoder)[0]
    output_dir = os.path.join('./output/' + encoder_name)
    mkdir_p(output_dir)
    image_name = os.path.splitext(os.path.basename(image))[0]
    image_out = os.path.join(output_dir, image_name + '_' + str(bpp_target) + '_' + pix_fmt + '.' + encoder_name)

    if os.path.isfile(image_out):
        print "\033[92m[ENCODE OK]\033[0m " + image_out
        return image_out
    encode_script = os.path.join('./encode/', encoder)
    cmd = [encode_script, image, image_out, str(bpp_target), width, height, pix_fmt, depth]
    try:
        print "\033[92m[ENCODING]\033[0m " + " ".join(cmd)
        subprocess.check_output(" ".join(cmd), stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print "\033[91m[ERROR]\033[0m " + e.output
        if os.path.isfile(image_out):
            os.remove(image_out)
        return
    if os.path.getsize(image_out) == 0:
        print "\033[91m[ERROR]\033[0m empty image: `" + image_out + "`, removing."
        print output
        os.remove(image_out)
        return
    else:
        return image_out

def decode(decoder, encoded_image, width, height, pix_fmt, depth):
    """ given a decoding script and a set of encoded images
        decode each image and place it in the ./output directory.
    """
    decoder_name = os.path.splitext(decoder)[0]
    output_dir = os.path.join('./output/', decoder_name, 'decoded')
    mkdir_p(output_dir)

    decode_script = os.path.join('./decode/', decoder)
    if pix_fmt == "ppm":
        ext_name = '.ppm'
    elif pix_fmt == "yuv420p":
        ext_name = '.yuv'
    decoded_image = os.path.join(output_dir, os.path.basename(encoded_image) + ext_name)
    if os.path.isfile(decoded_image):
        print "\033[92m[DECODE OK]\033[0m " + decoded_image
        return decoded_image
    cmd = [decode_script, encoded_image, decoded_image, width, height, pix_fmt]
    try:
        print "\033[92m[DECODING]\033[0m " + " ".join(cmd)
        subprocess.check_output(" ".join(cmd), stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print "\033[91m[ERROR]\033[0m " + e.output
        if os.path.isfile(decoded_image):
            os.remove(decoded_image)
        return
    if os.path.getsize(decoded_image) == 0:
        print "\033[91m[ERROR]\033[0m empty image: `" + image_out + "`, removing."
        print output
        os.remove(decoded_image)
    else:
        return decoded_image

def compute_vmaf(ref_image, dist_image, width, height, pix_fmt):
    """ given a pair of reference and distored images:
        use the ffmpeg libvmaf filter to compute vmaf, vif, ssim, and ms_ssim.
    """

    log_path = '/tmp/stats.json'
    cmd = ['ffmpeg', '-s:v', '%s,%s' % (width, height), '-i', dist_image,
            '-s:v', '%s,%s' % (width, height), '-i', ref_image,
            '-lavfi', 'libvmaf=ssim=true:ms_ssim=true:log_fmt=json:log_path=' + log_path,
            '-f', 'null', '-'
          ]

    try:
        print "\033[92m[VMAF]\033[0m " + dist_image
        subprocess.check_output(" ".join(cmd), stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print "\033[91m[ERROR]\033[0m " + " ".join(cmd) + "\n" + e.output

    vmaf_log = json.load(open(log_path))

    vmaf_dict = dict()
    vmaf_dict["vmaf"]    = vmaf_log["frames"][0]["metrics"]["vmaf"]
    vmaf_dict["vif"]     = vmaf_log["frames"][0]["metrics"]["vif_scale0"]
    vmaf_dict["ssim"]    = vmaf_log["frames"][0]["metrics"]["ssim"]
    vmaf_dict["ms_ssim"] = vmaf_log["frames"][0]["metrics"]["ms_ssim"]
    return vmaf_dict

def compute_psnr(ref_image, dist_image, width, height):
    """ given a pair of reference and distorted images:
        use the ffmpeg psnr filter to compute psnr and mse for each channel.
    """

    log_path = '/tmp/stats.log'
    cmd = ['ffmpeg', '-s:v', '%s,%s' % (width, height), '-i', dist_image,
            '-s:v', '%s,%s' % (width, height), '-i', ref_image,
            '-lavfi', 'psnr=stats_file=' + log_path,
            '-f', 'null', '-'
          ]

    try:
        print "\033[92m[PSNR]\033[0m " + dist_image
        subprocess.check_output(" ".join(cmd), stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print "\033[91m[ERROR]\033[0m " + e.output

    psnr_dict = dict()
    psnr_log = open(log_path).read()
    for stat in psnr_log.rstrip().split(" "):
        key, value = stat.split(":")
        if key is not "n":
            psnr_dict[key] = float(value)
    return psnr_dict

def compute_metrics(ref_image, dist_image, encoded_image, bpp_target, codec, width, height, pix_fmt):
    """ given a pair of reference and distorted images:
        call vmaf and psnr functions, dump results to a json file.
    """

    vmaf = compute_vmaf(ref_image, dist_image, width, height, pix_fmt)
    psnr = compute_psnr(ref_image, dist_image, width, height)
    stats = vmaf.copy()
    stats.update(psnr)
    return stats

def create_derivatives(image):
    """ given a test image, create ppm and yuv derivatives
    """
    name = os.path.basename(image).split(".")[0]
    derivative_images = []

    ppm_dir = os.path.join('derivative_images', 'ppm')
    ppm_dest = os.path.join(ppm_dir, name + '.ppm')
    if not os.path.isfile(ppm_dest):
        try:
            print "\033[92m[PPM]\033[0m " + ppm_dest
            mkdir_p(ppm_dir)
            cmd = ["ffmpeg", "-i", os.path.join('images', image), ppm_dest]
            subprocess.check_output(" ".join(cmd), stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            print cmd, e.output
            raise e
    else:
        print "\033[92m[PPM OK]\033[0m " + ppm_dest
    derivative_images.append((ppm_dest, 'ppm'))

    for subsampling in ['yuv420p']:
        yuv_dir = os.path.join('derivative_images', subsampling)
        yuv_dest = os.path.join(yuv_dir, name + '.yuv')
        if not os.path.isfile(yuv_dest):
            try:
                print "\033[92m[YUV]\033[0m " + yuv_dest
                mkdir_p(yuv_dir)
                cmd = ["ffmpeg", "-i", os.path.join('images', image), '-pix_fmt', subsampling, yuv_dest]
                subprocess.check_output(" ".join(cmd), stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                print cmd, e.output
                raise e
        else:
            print "\033[92m[YUV OK]\033[0m " + yuv_dest
        derivative_images.append((yuv_dest, subsampling))

    return derivative_images


def main():
    """ check for Docker, check for complementary encoding and decoding scripts, check for test images.
        fire off encoding and decoding scripts, followed by metrics computations.
    """
    error = False
    if not os.path.isfile('/.dockerenv'):
        print "\033[91m[ERROR]\033[0m" + " Docker is not detected. Run this script inside a container."
        error = True
    if not os.path.isdir('encode'):
        print "\033[91m[ERROR]\033[0m" + " No encode scripts directory `./encode`."
        error = True
    if not os.path.isdir('decode'):
        print "\033[91m[ERROR]\033[0m" + " No decode scripts directory `./decode`."
        error = True
    if not os.path.isdir('images'):
        print "\033[91m[ERROR]\033[0m" + " No source images directory `./images`."
        error = True
    if error:
        sys.exit(1)

    images = set(listdir_full_path('images'))
    if len(images) <= 0:
        print "\033[91m[ERROR]\033[0m" + " no source files in ./images."
        sys.exit(1)

    encoders = set(os.listdir('encode'))
    decoders = set(os.listdir('decode'))
    if encoders - decoders:
        print "\033[91m[ERROR]\033[0m" + " encode scripts without decode scripts:"
        for x in encoders - decoders: print "  - " + x
        error = True
    if decoders - encoders:
        print "\033[91m[ERROR]\033[0m" + " decode scripts without encode scripts:"
        for x in decoders - encoders: print "  - " + x
        error = True
    if error:
        sys.exit(1)

    bpp_targets = set([0.12, 0.25, 0.50, 0.75, 1.00, 1.50, 2.00])

    for image in images:
        width, height, depth = get_dimensions(image)
        derivative_images = create_derivatives(image)
        for derivative_image, pix_fmt in derivative_images:
            json_dir = 'metrics'
            json_file = os.path.join(json_dir, os.path.splitext(os.path.basename(derivative_image))[0] + "." + pix_fmt + ".json")
            if os.path.isfile(json_file):
                print "\033[92m[JSON OK]\033[0m " + json_file
                continue
            main_dict = dict()
            derivative_image_metrics = dict()
            for codec in encoders | decoders:
                bpp_target_metrics = dict()
                for bpp_target in bpp_targets:
                    encoded_image = encode(codec, bpp_target, derivative_image, width, height, pix_fmt, depth)
                    if encoded_image is None:
                        continue
                    decoded_image = decode(codec, encoded_image, width, height, pix_fmt, depth)
                    metrics = compute_metrics(derivative_image, decoded_image, encoded_image, bpp_target, codec, width, height, pix_fmt)
                    measured_bpp = (os.path.getsize(encoded_image) * 8) / (float((int(width) * int(height))))
                    bpp_target_metrics[measured_bpp] = metrics
                derivative_image_metrics[os.path.splitext(codec)[0]] = bpp_target_metrics
            main_dict[derivative_image] = derivative_image_metrics

            mkdir_p(json_dir)
            with open(json_file, 'w') as f:
                f.write(json.dumps(main_dict, indent=2))

if __name__ == "__main__":
    main()
