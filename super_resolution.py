import argparse
import os
import sys

from system import call_subprocess

DEFAULT_MODEL = "realesr-animevideov3"
DEFAULT_SCALE = "2"
DEFAULT_FORMAT = 'jpg'

def process_output(line, amount):
    file = line.split()[0]
    filename = os.path.basename(file)
    os.rename(file, os.path.join(os.path.dirname(file)+"-sr-done", filename))
    n = int("".join([x for x in filename if x.isdigit()]))
    sys.stdout.write(f"Super Resolution {n}/{amount} {file}\r")
    if n == amount:
        sys.stdout.write(f"Super Resolution {n}/{amount} {file}\n")

def realesrgan(source, destination=None):

    dest = source+"-sr"
    if destination:
        dest = destination
    os.makedirs(dest, exist_ok=True)
    os.makedirs(source+"-sr-done", exist_ok=True)

    amount = len(os.listdir(source))
    amount += len(os.listdir(source+"-sr-done"))

    call_subprocess(["./realesrgan-ncnn-vulkan/realesrgan-ncnn-vulkan", "-i", source, "-o", dest, "-n", DEFAULT_MODEL, "-s", DEFAULT_SCALE, "-f", DEFAULT_FORMAT, "-v"], patterns=[" -> "], pattern_callback=process_output, callback_conext={"amount": amount})

    os.rmdir(source)
    os.rename(source+"-sr-done", source)

    return dest

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, help='Source folder path')
    parser.add_argument('--destination', '-d', type=str, required=False, help='Destination folder path')
    args = parser.parse_args()

    realesrgan(args.source, args.destination)