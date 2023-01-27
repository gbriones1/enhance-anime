import argparse
import os
import sys

from system import call_subprocess

DEFAULT_MODEL = "rife-anime"
DEFAULT_FORMAT = 'jpg'
DEFAULT_SCALE = 2

def process_output(line, amount):
    file = line.split()[-2]
    filename = os.path.basename(file)
    # os.rename(file, os.path.join(os.path.dirname(file)+"-interp-done", filename))
    n = int("".join([x for x in filename if x.isdigit()]))
    sys.stdout.write(f"Interpolation {n}/{amount} {file}\r")
    if n == amount:
        sys.stdout.write(f"Interpolation {n}/{amount} {file}\n")

def rife(source, destination=None, model: str=DEFAULT_MODEL, scale=DEFAULT_SCALE):

    dest = source+"-interp"
    if destination:
        dest = destination
    os.makedirs(dest, exist_ok=True)
    # os.makedirs(source+"-interp-done", exist_ok=True)

    amount = len(os.listdir(source))
    # amount += len(os.listdir(source+"-interp-done"))

    cmd = ["./rife-ncnn-vulkan/rife-ncnn-vulkan", "-i", source, "-o", dest, "-m", model, "-f", DEFAULT_FORMAT, "-v", "-n", f"{int(amount*scale)}"]

    call_subprocess(cmd, patterns=[" -> "], pattern_callback=process_output, callback_conext={"amount": int(amount*scale)})

    # if len(os.listdir(source)) == 1:
    #     os.rename(os.path.join(source, os.listdir(source)[0]), os.path.join(source+"-interp-done", os.listdir(source)[0]))

    # os.rmdir(source)
    # os.rename(source+"-interp-done", source)

    return dest

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, help='Source folder path')
    parser.add_argument('--destination', '-d', type=str, required=False, help='Destination folder path')
    args = parser.parse_args()

    rife(args.source, args.destination)