import argparse
import glob
import os
import sys

DEFAULT_START = 2
DEFAULT_OFFSET = 5

def decrease(source, start=DEFAULT_START, offset=DEFAULT_OFFSET):

    files = sorted(glob.glob(os.path.join(source, '*.*')))
    for n, file in enumerate(files[:]):
        action = 'kept back'
        if (n+2+start) % offset == 0:
            action = 'removed'
            os.remove(file)

        sys.stdout.write(f"Frame rate reduce {n+1}/{len(files)} {file} {action}\r")
    sys.stdout.write(f"Frame rate reduce {n+1}/{len(files)} {file} {action}\n")
    
    files = sorted(glob.glob(os.path.join(source, '*.*')))
    for n, file in enumerate(files[:]):
        filename = os.path.basename(file)
        frame_name = '.'.join(filename.split('.')[:-1])[:-8]
        ext = filename.split('.')[-1]
        os.rename(file, os.path.join(os.path.dirname(file), f"{frame_name}{n+1:08d}.{ext}"))

        sys.stdout.write(f"Frame rate rename {n+1}/{len(files)} {file} {n+1}\r")
    sys.stdout.write(f"Frame rate rename {n+1}/{len(files)} {file} {n+1}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, help='Source folder path')
    parser.add_argument('--start', type=int, required=False, default=DEFAULT_START, help='Starting frame to be removed')
    parser.add_argument('--offset', type=int, required=False, default=DEFAULT_OFFSET, help='Offset for frames to be removed')
    args = parser.parse_args()

    decrease(args.source, args.start, args.offset)
