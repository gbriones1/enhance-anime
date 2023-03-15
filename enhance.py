import argparse
import glob
import os
import shutil
import time

from video_codec import decode, encode
from framerate import decrease
from shape import reshape
from super_resolution import realesrgan
from interpolation import rife, DEFAULT_SCALE

DEFAULT_WORKDIR = './workdir'

def process(workdir=DEFAULT_WORKDIR, config={}):

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
                source = decode(file)
                preprocess_fr = config.get('preprocess_fr')
                if preprocess_fr:
                    decrease(source, **preprocess_fr)
                preprocess_shape = config.get('preprocess_shape')
                if preprocess_shape:
                    reshape(source, **preprocess_shape)
                os.rename(source, target)
            source = target

            target = source+"-sr"
            if not os.path.exists(target) or os.path.exists(target+"-done"):
                sr = config.get('sr', {})
                if config.get('intro') and os.path.exists(os.path.join(workdir, 'intro-sr')):
                    sr['intro'] = os.path.join(workdir, 'intro-sr')
                if config.get('outro') and os.path.exists(os.path.join(workdir, 'outro-sr')):
                    sr['outro'] = os.path.join(workdir, 'outro-sr')
                source = realesrgan(source, **sr)
                if config.get('intro') and not os.path.exists(os.path.join(workdir, 'intro-sr')):
                    os.makedirs(os.path.join(workdir, 'intro-sr'))
                    for file in glob.glob(os.path.join(source, '*.*'))[:config.get('intro')]:
                        shutil.copy2(file, os.path.join(workdir, 'intro-sr'))
                os.rename(source, target)
            source = target

            target = source+"-interp"
            fr_scale = config.get('interp', {}).get('scale', DEFAULT_SCALE)
            if not os.path.exists(target) or len(os.listdir(target)) < int(len(os.listdir(source))*fr_scale):
                interp = config.get('interp', {})
                # if config.get('intro') and os.path.exists(os.path.join(workdir, 'intro-interp')):
                #     interp['intro'] = os.path.join(workdir, 'intro-interp')
                source = rife(source, **interp)
                # if config.get('intro') and not os.path.exists(os.path.join(workdir, 'intro-interp')):
                #     os.makedirs(os.path.join(workdir, 'intro-interp'))
                #     for file in glob.glob(os.path.join(source, '*.*'))[:config.get('intro')*fr_scale]:
                #         shutil.copy2(file, os.path.join(workdir, 'intro-interp'))
                os.rename(source, target)
            source = target
        
            result = encode(source, file, destination=results_dir, prefix="", **config.get('encoder', {}))
            os.rename(result, os.path.join(results_dir, video_name+".mkv"))

        if config.get('cleanup', True):
            for suffix in ["", "-sr", "-sr-interp", "-interp"]:
                if os.path.exists(os.path.join(workdir, video_name+suffix)):
                    shutil.rmtree(os.path.join(workdir, video_name+suffix))

        print("Finished", f"{n+1}/{len(files)}", file, f"{(time.time()-start_time)/60:.2f}m")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--workdir', '-w', type=str, required=False, default=DEFAULT_WORKDIR, help='Source folder path')
    args = parser.parse_args()

    config = {
        'intro': 2278,
        'outro': 30092,
        'cleanup': True,
        'preprocess_fr': {
            'start': 2,
            'offset': 5
        },
        'preprocess_shape': {
            'width': 640,
            'height': 480
        },
        'interp': {
            'scale': 2.5
        },
        'encoder': {
            'framerate': '60000/1001',
            'encoder_params': ["-crf", "26", "-preset", "slow", "-x265-params", "profile=main10"]
        }
    }
    
    config = {
        'intro': 1909,
        'outro': 32009,
        'cleanup': False,
        'preprocess_shape': {
            'width': 640,
            'height': 480
        },
        'interp': {
            'scale': 2.5
        },
        'encoder': {
            'framerate': '60000/1001',
            'encoder_params': ["-crf", "26", "-preset", "slow", "-x265-params", "profile=main10"]
        }
    }


    process(args.workdir, config=config)
