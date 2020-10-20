import os
import shutil
import random

INP_DIR = 'data/ocr/back_cmtnd_resized/'
OUT_DIR = 'data/ocr/test/'

dir = os.listdir(INP_DIR)
dir = [x for x in dir if x.endswith('jpg')]
dir = random.sample(dir, 100)
dir.sort()

f = open(os.path.join(OUT_DIR, 'test.txt'), 'w')

for fi in dir:
    print(fi)
    img_path = os.path.join(INP_DIR, fi)
    fn, _ = os.path.splitext(fi)
    label_path = os.path.join(INP_DIR, fn + '.txt')
    if not os.path.isfile(label_path): continue
    out_img_path = os.path.join(OUT_DIR, fi)
    out_label_path = os.path.join(OUT_DIR, fn + '.txt')
    shutil.copyfile(img_path, out_img_path)
    # shutil.copyfile(label_path, out_label_path)
    f.write(out_img_path + '\n')

f.close()