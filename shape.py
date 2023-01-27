import argparse
import glob
import os
import sys

import cv2
import numpy as np

DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480

def reshape(source, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, destination=None):

    dest = source
    if destination:
        dest = destination
        os.makedirs(dest)

    files = sorted(glob.glob(os.path.join(source, '*.*')))
    for n, file in enumerate(files[:]):
        filename = os.path.basename(file)
        img_name = '.'.join(filename.split('.')[:-1])

        img = cv2.imread(file, cv2.IMREAD_COLOR) # BGR
        if not isinstance(img, np.ndarray): print(filename, 'error'); continue

        img = cv2.resize(img, (width, height), interpolation = cv2.INTER_AREA)

        cv2.imwrite(os.path.join(dest, f'{img_name}.jpg'), img)

        sys.stdout.write(f"Reshape {n+1}/{len(files)} {file} {img.shape}\r")
    sys.stdout.write(f"Reshape {n+1}/{len(files)} {file} {img.shape}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, help='Source folder path')
    parser.add_argument('--width', type=int, required=False, default=DEFAULT_WIDTH, help='Width of the outputs')
    parser.add_argument('--height', type=int, required=False, default=DEFAULT_HEIGHT, help='Height of the outputs')
    parser.add_argument('--destination', '-d', type=str, required=False, help='Destination folder path')
    args = parser.parse_args()

    reshape(args.source, args.width, args.height, args.destination)


