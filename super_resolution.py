import argparse
import glob
import os
import shutil
import sys

from recycling import find_img
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

def recycle_intro(source, intro, dest):
    for file in sorted(glob.glob(os.path.join(intro, '*.*'))):
        shutil.copy2(file, dest)
        filename = os.path.basename(file)
        if not os.path.exists(os.path.join(source+"-sr-done", filename)):
            os.rename(os.path.join(source, filename), os.path.join(source+"-sr-done", filename))
        sys.stdout.write(f"Recycling intro {os.path.join(source, filename)} -> {os.path.join(source+'-sr-done', filename)}\r")
    sys.stdout.write(f"Recycling intro {os.path.join(source, filename)} -> {os.path.join(source+'-sr-done', filename)}\n")

def recycle_outro(source, outro, dest):
    outro_files = sorted(glob.glob(os.path.join(outro, '*.*')))
    source_outro = find_img(outro_files[0], source, margin=200)
    if source_outro:
        source_number = "".join([x for x in os.path.basename(source_outro) if x.isdigit()])
        source_start = int(source_number)
        source_prefix = source_outro.split(source_number)

        count = source_start
        for file in outro_files:
            new_filename = os.path.basename("".join([source_prefix[0], f"{count:08d}", source_prefix[1]]))
            shutil.copy2(file, os.path.join(dest, new_filename))
            count += 1

        for frame in range(source_start, source_start+len(outro_files)):
            file = "".join([source_prefix[0], f"{frame:08d}", source_prefix[1]])
            filename = os.path.basename(file)
            if not os.path.exists(os.path.join(source+"-sr-done", filename)):
                print(os.path.join(source, filename))
                os.rename(os.path.join(source, filename), os.path.join(source+"-sr-done", filename))
            sys.stdout.write(f"Recycling outtro {os.path.join(source, filename)} -> {os.path.join(source+'-sr-done', filename)}\r")
        sys.stdout.write(f"Recycling outro {os.path.join(source, filename)} -> {os.path.join(source+'-sr-done', filename)}\n")

def realesrgan(source, destination=None, intro=None, outro=None):

    dest = source+"-sr"
    if destination:
        dest = destination
    os.makedirs(dest, exist_ok=True)
    os.makedirs(source+"-sr-done", exist_ok=True)

    if intro:
        recycle_intro(source, intro, dest)
    
    if outro:
        recycle_outro(source, outro, dest)

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