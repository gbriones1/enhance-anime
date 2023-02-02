import glob
import os
import sys

import cv2
import numpy as np
from skimage.metrics import structural_similarity


def mse(img1, img2):
   h, w = img1.shape
   diff = cv2.subtract(img1, img2)
   err = np.sum(diff**2)
   mse = err/(float(h*w))
   return mse


def find_img(img_file, folder, margin=None):
    img1 = cv2.imread(img_file)
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    if not isinstance(img1, np.ndarray): print(img_file, 'error'); exit(1)
    frame = int("".join([x for x in os.path.basename(img_file) if x.isdigit()]))

    errors =  {}

    files = sorted(glob.glob(os.path.join(folder, '*.*')))
    for n, file in enumerate(files[:]):
        filename = os.path.basename(file)
        img_frame = int("".join([x for x in filename if x.isdigit()]))
        if margin and (img_frame <= frame-margin or img_frame >= frame+margin):
            continue
        img2 = cv2.imread(file)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        if not isinstance(img2, np.ndarray): print(filename, 'error'); continue

        img1 = cv2.resize(img1, (img2.shape[1], img2.shape[0]), interpolation = cv2.INTER_AREA)

        simm = structural_similarity(img1, img2)

        errors[simm] = file
        sys.stdout.write(f"Finding simmilar {img_file} -> {file}: {simm:.2f}\r")
    sys.stdout.write(f"\n")


    max_ = max(errors.keys())
    # print("Max:", max_, errors[max_])
    # min_ = min(errors.keys())
    # print("Min:", min_, errors[min_])

    # print("Best 10:")
    # for best in sorted(errors.keys(), reverse=True)[:10]:
    #     print(best, errors[best])
    # print("Worst 10:")
    # for worst in sorted(errors.keys(), reverse=False)[:10]:
    #     print(worst, errors[worst])
    if max_ < 0.9:
        print("Similar not found")
        return
    return errors[max_]


# find_img('workdir/S01E05-sr/frame00030092.jpg', 'workdir/S01E05', margin=500)