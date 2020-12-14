from __future__ import print_function
from __future__ import division

from datetime import datetime

import cv2 as cv
import numpy as np
import argparse
import os

from django.conf import settings

root_path = settings.MEDIA_ROOT

now = datetime.now()
date_time = now.strftime("%m_%d_%Y_%H_%M_%S")

out_file_name = 'hdr' + date_time + '.jpg'


# OUT_FILE = os.path.join(settings.MEDIA_ROOT, out_file_name)

def loadExposureSeq(path):
    images = []
    times = []
    with open(os.path.join(path, 'list.txt')) as f:
        content = f.readlines()
    for line in content:
        tokens = line.split()
        images.append(cv.imread(os.path.join(root_path, tokens[0])))
        times.append(1 / float(tokens[1]))
    return images, np.asarray(times, dtype=np.float32)


def run():
    images, times = loadExposureSeq(settings.BASE_DIR)
    calibrate = cv.createCalibrateDebevec()
    response = calibrate.process(images, times)

    merge_debevec = cv.createMergeDebevec()
    hdr = merge_debevec.process(images, times, response)

    tonemap = cv.createTonemap(2.2)
    ldr = tonemap.process(hdr)

    merge_mertens = cv.createMergeMertens()
    fusion = merge_mertens.process(images)

    out_file_name = 'fusion' + date_time + '.png'
    OUT_FILE = os.path.join(settings.HDR_ROOT, out_file_name)
    cv.imwrite(OUT_FILE, fusion * 255)
    # cv.imwrite(root_path'ldr.png', ldr * 255)
    # cv.imwrite('hdr.hdr', hdr)
