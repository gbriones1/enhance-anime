import argparse
import glob
import os
import shutil
import time

from video_codec import decode, encode
from framerate import decrease
from shape import reshape
from super_resolution import realesrgan
from interpolation import rife

DEFAULT_SOURCE = './workdir'

def preprocess(file):
    source = decode(file)
    decrease(source)
    reshape(source)
    return source

def process(workdir=DEFAULT_SOURCE):

    results_dir = os.path.join(workdir, "results")
    os.makedirs(results_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(workdir, '*.*')))
    for n, file in enumerate(files[:]):

        start_time = time.time()

        filename = os.path.basename(file)
        video_name = '.'.join(filename.split('.')[:-1])
        if not os.path.exists(os.path.join(results_dir, video_name+".mkv")):

            target = os.path.join(workdir, video_name)
            if not os.path.exists(target):
                source = preprocess(file)
                os.rename(source, target)
            source = target

            target = source+"-sr"
            if not os.path.exists(target) or os.path.exists(target+"-done"):
                source = realesrgan(source)
                os.rename(source, target)
            source = target

            target = source+"-interp"
            if not os.path.exists(target) or len(os.listdir(target)) < int(len(os.listdir(source))*2.5):
                source = rife(source, model="rife-v4.6", scale=2.5)
                os.rename(source, target)
            source = target
        
            result = encode(source, file, destination=results_dir, framerate="60000/1001", prefix="")
            os.rename(result, os.path.join(results_dir, video_name+".mkv"))

        # for suffix in ["", "-sr", "-sr-interp", "-interp"]:
        #     if os.path.exists(os.path.join(workdir, video_name+suffix)):
        #         shutil.rmtree(os.path.join(workdir, video_name+suffix))

        print("Finished", f"{n+1}/{len(files)}", file, f"{(time.time()-start_time)/60:.2f}m")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--workdir', '-w', type=str, required=False, default=DEFAULT_SOURCE, help='Source folder path')
    args = parser.parse_args()

    process(args.workdir)
