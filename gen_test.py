import os
import shutil
import xml.etree.ElementTree as ET
from random import randint
from time import time

IMG_DIR = "/dataset/upload_complete"

OUT_DIR = "/storage/data/test/"
os.makedirs(OUT_DIR, exist_ok=True)

dir = os.listdir(IMG_DIR)
dir.sort()

fo = open(os.path.join(OUT_DIR, 'test.txt'), 'w')
for fi in dir:
    src = os.path.join(IMG_DIR, fi)
    dst = os.path.join(OUT_DIR, fi)
    shutil.copyfile(src, dst)
    fo.write(dst + '\n')
fo.close()
    